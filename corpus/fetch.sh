#!/usr/bin/env bash
# Fetch the public-domain corpus files listed in SOURCES.md into corpus/files/.
# Files are not committed to git (see .gitignore); this script is the
# reproducible path for judges. All works are public domain (pre-1930 or US gov).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p files/nigeria files/polar

fetch() { # fetch <url> <dest>
  if [ -s "$2" ]; then echo "exists: $2"; else
    echo "fetching: $2"
    curl -sSL --fail --retry 3 --retry-delay 2 -o "$2" "$1"
  fi
}

# --- Field 1: Colonial-era Northern Nigeria / Sokoto Caliphate ---
fetch "https://archive.org/download/makingofnorthern00orrc/makingofnorthern00orrc_djvu.txt" \
      "files/nigeria/orr_making_of_northern_nigeria_1911.txt"
fetch "https://archive.org/download/makingofnorthern00orrc/makingofnorthern00orrc.pdf" \
      "files/nigeria/orr_making_of_northern_nigeria_1911.pdf"
fetch "https://archive.org/download/tropicaldependen00luga/tropicaldependen00luga_djvu.txt" \
      "files/nigeria/shaw_a_tropical_dependency_1905.txt"

# --- Field 2: Forgotten 19th-century polar expeditions ---
fetch "https://www.gutenberg.org/cache/epub/6137/pg6137.txt" \
      "files/polar/mawson_home_of_the_blizzard_1915.txt"
fetch "https://archive.org/download/voyageofjeannett01delo/voyageofjeannett01delo_djvu.txt" \
      "files/polar/delong_voyage_of_the_jeannette_v1_1884.txt"
fetch "https://archive.org/download/threeyearsofarct00greeuoft/threeyearsofarct00greeuoft_djvu.txt" \
      "files/polar/greely_three_years_of_arctic_service_v1_1886.txt"

echo "done."; ls -la files/nigeria files/polar

# --- Field 1 additions (Phase 0.3) ---
fetch "https://archive.org/download/hausaland00robi/hausaland00robi_djvu.txt" \
      "files/nigeria/robinson_hausaland_1896.txt"
fetch "https://archive.org/download/nigeriaitspeople00more/nigeriaitspeople00more_djvu.txt" \
      "files/nigeria/morel_nigeria_peoples_problems_1911.txt"
fetch "https://www.gutenberg.org/cache/epub/73138/pg73138-images.html" \
      "files/nigeria/barth_travels_north_central_africa_gutenberg.html"
