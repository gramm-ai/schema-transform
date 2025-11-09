"""
Generate SVG diagrams from Mermaid code
Uses mermaid.ink API to convert Mermaid to SVG
"""
import base64
import urllib.request
import urllib.parse
from pathlib import Path
import zlib


def mermaid_to_svg(mermaid_code: str) -> str:
    """
    Convert Mermaid code to SVG using mermaid.ink API

    Args:
        mermaid_code: Mermaid diagram code

    Returns:
        SVG content as string
    """
    # Encode mermaid code
    encoded = base64.urlsafe_b64encode(
        zlib.compress(mermaid_code.encode('utf-8'), 9)
    ).decode('ascii')

    # Generate URL
    url = f"https://mermaid.ink/svg/{encoded}"

    # Fetch SVG
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            svg_content = response.read().decode('utf-8')
        return svg_content
    except Exception as e:
        print(f"Error fetching SVG: {e}")
        return None


def generate_all_diagrams():
    """Generate SVG files for all Mermaid diagrams"""

    # Paths
    diagram_dir = Path("/proj/sprint/schema-translator/docs/assets")

    # Find all .mmd files
    mermaid_files = list(diagram_dir.glob("*.mmd"))

    print(f"Found {len(mermaid_files)} Mermaid diagram(s)")

    for mmd_file in mermaid_files:
        print(f"\nProcessing: {mmd_file.name}")

        # Read Mermaid code
        with open(mmd_file, 'r') as f:
            mermaid_code = f.read()

        # Generate SVG
        svg_content = mermaid_to_svg(mermaid_code)

        if svg_content:
            # Save SVG
            svg_file = mmd_file.with_suffix('.svg')
            with open(svg_file, 'w') as f:
                f.write(svg_content)

            print(f"✅ Generated: {svg_file.name}")
        else:
            print(f"❌ Failed to generate SVG for {mmd_file.name}")


if __name__ == "__main__":
    generate_all_diagrams()
