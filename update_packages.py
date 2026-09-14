#!/usr/bin/env python3
"""
越狱源 Packages 索引生成脚本（纯 Python，无需 dpkg-deb）
支持: .deb (ar + gzip/xz 压缩的 control.tar)
用法: python3 update_packages.py
"""
import gzip, hashlib, bz2, lzma
from pathlib import Path

REPO_DIR = Path(__file__).parent
DEBS_DIR = REPO_DIR / "debs"
OUT_PKGS = REPO_DIR / "Packages"
OUT_PKGS_BZ2 = REPO_DIR / "Packages.bz2"

# ────────────────────────── 纯 Python deb 解析 ──────────────────────────

def read_ar_member(data: bytes, offset: int):
    """解析一个 ar member header（60字节标准格式）"""
    hdr = data[offset:offset + 60]
    if len(hdr) < 60 or hdr[58:60] != b'`\n':
        return None, None, None
    try:
        size = int(hdr[48:58].rstrip(b' '))
    except ValueError:
        return None, None, None
    name_str = hdr[0:16].rstrip(b' /').decode('ascii', errors='replace').strip()
    member_data = data[offset + 60:offset + 60 + size]
    next_off = offset + 60 + size + ((size + 1) // 2 * 2 - size)  # pad to even
    return name_str, member_data, next_off

def parse_control_in_tar(tar_data: bytes) -> dict:
    """
    从 control.tar (gzip/xz) 中提取 control 文件内容。
    支持: PAX (全局头) + 标准 ustar + GNU tar longname
    """
    info = {}

    # ── 方法A: 直接搜索 "Package:" 字节序列（最可靠兜底） ──
    raw = tar_data
    pkg_idx = raw.find(b'Package:')
    if pkg_idx >= 0:
        # 往前找行首，往后取足够长
        line_start = max(0, raw.rfind(b'\n', 0, pkg_idx))
        chunk = raw[line_start:pkg_idx + 1500]
        text = chunk.decode('utf-8', errors='replace')
        for line in text.splitlines():
            line = line.strip()
            if ':' not in line:
                continue
            k, _, v = line.partition(':')
            k = k.strip()
            v = v.strip()
            if k in ('Package', 'Version', 'Architecture', 'Description',
                     'Maintainer', 'Author', 'Section', 'Depends', 'Name',
                     'Pre-Depends', 'Recommends', 'Conflicts', 'Provides',
                     'Replaces', 'Filename'):
                info[k] = v
        # PAX tar: 如果 Package 没被加进去，从 pkg_idx 直接起读
        if 'Package' not in info and pkg_idx >= 0:
            ctrl_text = tar_data[pkg_idx:pkg_idx + 2000].decode('utf-8', errors='replace')
            for line in ctrl_text.splitlines():
                line = line.strip()
                if ':' not in line:
                    continue
                k, _, v = line.partition(':')
                k = k.strip()
                v = v.strip()
                if k in ('Package', 'Version', 'Architecture', 'Description',
                         'Maintainer', 'Author', 'Section', 'Depends', 'Name'):
                    info[k] = v
        if info:
            return info

    # ── 方法B: 标准 tar 遍历（名字匹配 "control"） ──
    pos = 0
    while pos + 512 <= len(raw):
        # 找文件名（最多扫 100 字节，跳过前导特殊情况）
        chunk = raw[pos:pos + 512]
        # 标准 ustar: name at 0-100, prefix at 345-500
        name_raw = chunk[0:100].rstrip(b'\x00 ')
        prefix_raw = chunk[345:500].rstrip(b'\x00 ')
        try:
            name = name_raw.decode('ascii', errors='replace').strip()
            prefix = prefix_raw.decode('ascii', errors='replace').strip()
        except Exception:
            pos += 512
            continue
        # GNU tar longlink: ././@LongLink or 0/...
        if name == '././@LongLink' or name.startswith('0/'):
            size_raw = chunk[124:136]
            try:
                size = int(size_raw.strip(), 8)
            except ValueError:
                pos += 512
                continue
            pos += 512 + ((size + 511) // 512) * 512
            continue
        # 正常条目
        size_raw = chunk[124:136]
        try:
            size = int(size_raw.strip(), 8)
        except ValueError:
            pos += 512
            continue
        # 跳过全零 header
        if name == '' and size == 0:
            pos += 512
            continue
        full_name = (prefix + '/' + name).strip('/') if prefix else name
        if full_name.endswith('control') or full_name == 'control':
            fc = raw[pos + 512:pos + 512 + size]
            for line in fc.decode('utf-8', errors='replace').splitlines():
                line = line.strip()
                if ':' not in line:
                    continue
                k, _, v = line.partition(':')
                k = k.strip()
                v = v.strip()
                if k in ('Package', 'Version', 'Architecture', 'Description',
                         'Maintainer', 'Author', 'Section', 'Depends', 'Name'):
                    info[k] = v
            return info
        pos += 512 + ((size + 511) // 512) * 512

    return info

def parse_deb_control(deb_path: Path) -> dict:
    """纯 Python 解析 deb 的 control 信息"""
    raw = deb_path.read_bytes()
    info = {"Size": str(deb_path.stat().st_size)}
    offset = 8  # skip "!<arch>\n"

    while offset < len(raw):
        name_str, member_data, next_off = read_ar_member(raw, offset)
        if name_str is None:
            break
        if name_str in ("control.tar.gz", "control.tar.xz", "control.tar"):
            try:
                if name_str == "control.tar.gz":
                    tar_data = gzip.decompress(member_data)
                elif name_str in ("control.tar.xz", "control.tar"):
                    tar_data = lzma.decompress(member_data)
                else:
                    offset = next_off
                    continue
            except Exception:
                offset = next_off
                continue
            ctrl = parse_control_in_tar(tar_data)
            if ctrl:
                info.update(ctrl)
                break
        offset = next_off

    info["Filename"] = f"debs/{deb_path.name}"
    return info

def md5_hex(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def build_packages_text(debs_dir: Path) -> str:
    lines = []
    for deb in sorted(debs_dir.glob("*.deb")):
        try:
            info = parse_deb_control(deb)
            stem = info.get('Package','?').split('.')[-1]
            info['Depiction']       = f'https://MrSuuu.github.io/Sileo/depictions/{stem}.html'
            info['SileoDepiction']  = info['Depiction']
            for key in ["Package", "Name", "Version", "Architecture", "Description",
                        "Maintainer", "Author", "Depiction", "SileoDepiction", "Section", "Depends",
                        "Filename", "Size"]:
                if key in info:
                    lines.append(f"{key}: {info[key]}")
            lines.append(f"MD5sum: {md5_hex(deb)}")
            lines.append(f"SHA256: {sha256_hex(deb)}")
            lines.append("")
            pkg = info.get('Package', '?')
            ver = info.get('Version', '?')
            print(f"  ✅ {deb.name}  [{pkg} {ver}]")
        except Exception as e:
            print(f"  ⚠️ 跳过 {deb.name}: {e}")
    return "\n".join(lines)

def main():
    print("📦 生成越狱源索引...\n")
    debs = list(DEBS_DIR.glob("*.deb"))
    print(f"  找到 {len(debs)} 个 deb\n")
    print("  生成 Packages...")
    pkg_text = build_packages_text(DEBS_DIR)
    OUT_PKGS.write_text(pkg_text, encoding="utf-8")
    print(f"\n  ✅ Packages ({len(pkg_text):,} bytes)")
    print("\n  生成 Packages.bz2...")
    bz2_data = bz2.compress(pkg_text.encode("utf-8"))
    OUT_PKGS_BZ2.write_bytes(bz2_data)
    print(f"  ✅ Packages.bz2 ({len(bz2_data):,} bytes)")
    # 生成 Packages.gz（Cydia / Zebra 兼容）
    import gzip as _gzip
    gz_path = REPO_DIR / "Packages.gz"
    with _gzip.open(gz_path, "wb", compresslevel=9) as f:
        f.write(pkg_text.encode("utf-8"))
    print(f"  ✅ Packages.gz ({gz_path.stat().st_size:,} bytes)")
    print("\n🎉 完成！")

if __name__ == "__main__":
    main()
