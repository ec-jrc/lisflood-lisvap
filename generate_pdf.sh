#!/usr/bin/env bash
yaml_header="---
  # ...
  header-includes:
    - \newcommand{\gt}{>}
    - \newcommand{\lt}{<}
  # ...
---
"

mkdir -p ./_pdf/
mkdir -p ./_pdf/media
rm ./_pdf/*.md 2> /dev/null
rm ./_pdf/*.pdf 2> /dev/null
rm ./_pdf/media/* 2> /dev/null
cp -R ./media/* ./_pdf/media/

for dir in ./_site/*;
do
  if [[ -d "${dir}" && ! -L "${dir}" ]]; then
    dir=${dir%*/}
    fin=${dir##*/}
    if [[ "$fin" != "media" && "$fin" != "assets" && "$fin" != "index_old" && "$fin" != "everything" && "$fin" != "index_UserGuide" && "$fin" != "index_pdf" ]]; then
      echo "-----> ${fin}"
      cp ${dir}/index.md ./_pdf/${fin}.md
      sed -i 's#\.\./media/#\./media/#g' ./_pdf/${fin}.md
    fi
  fi
done

echo "pandoc index_pdf.md --normalize --smart --template=template.latex -o _pdf/frontpage.pdf -V geometry:margin=1.5cm"
pandoc index_pdf.md --normalize --smart --template=template.latex -o _pdf/frontpage.pdf -V geometry:margin=1.5cm
echo "pandoc _pdf/*.md --normalize --smart --toc -V toc-title:"Table of Contents" --template=template.latex -f markdown+tex_math_dollars+tex_math_single_backslash --latex-engine=xelatex -o _pdf/manual.pdf -V geometry:margin=1.5cm"
pandoc _pdf/*.md --normalize --smart --toc -V toc-title:"Table of Contents" --template=template.latex -f markdown+tex_math_dollars+tex_math_single_backslash --latex-engine=xelatex -o _pdf/manual.pdf -V geometry:margin=1.5cm

echo "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/None -sOutputFile=./_pdf/Lisvap_Model.pdf ./_pdf/frontpage.pdf ./_pdf/manual.pdf"
#pdftk ./_pdf/frontpage.pdf ./_pdf/manual.pdf cat output ./_pdf/Lisflood_Model.pdf
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -dAutoRotatePages=/None -sOutputFile=./_pdf/Lisvap_Model.pdf ./_pdf/frontpage.pdf ./_pdf/manual.pdf
cp ./_pdf/Lisvap_Model.pdf ./
cp ./_pdf/Lisvap_Model.pdf ./_site/
