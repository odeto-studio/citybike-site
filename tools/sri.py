"""Bundle each island (plus any CSS it injects) into dist/ and print its sha384 SRI for Webflow's hosted-script registration.
Run: python3 -I tools/sri.py [island ...]   (no args = every islands/*.js)"""
import base64
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
DIST = HERE / "dist"


def main():
    names = sys.argv[1:] or [p.stem for p in sorted((HERE / "islands").glob("*.js"))]
    DIST.mkdir(exist_ok=True)
    for name in names:
        body = (HERE / "islands" / f"{name}.js").read_bytes()
        (DIST / f"{name}.js").write_bytes(body)
        sri = "sha384-" + base64.b64encode(hashlib.sha384(body).digest()).decode()
        print(f"{name}.js  {len(body)} B  {sri}")


main()
