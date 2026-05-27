#!/bin/bash
#
# Re-extract all lectures using the improved extractor
# This should recover content from sections that were previously truncated.

set -e

echo "=== Re-extraindo todas as palestras com o extrator melhorado ==="
echo ""

# Install dependencies if needed
echo "Instalando/atualizando dependências..."
pip3 install beautifulsoup4 markdownify --quiet 2>/dev/null || pip install beautifulsoup4 markdownify --quiet 2>/dev/null

echo ""
echo "Reextraindo todas as 16 palestras..."
python3 scripts/extract_transcript.py --all

echo ""
echo "=== Extração concluída! ==="
echo ""
echo "Próximos passos recomendados:"
echo "1. Verifique as palestras que tinham seções muito curtas (especialmente a 02)."
echo "2. Compare as novas versões em inglês com as traduções PT-BR."
echo "3. Atualize as traduções PT-BR onde o conteúdo foi recuperado."
echo ""
echo "Para executar a extração manualmente (se preferir):"
echo "  python3 scripts/extract_transcript.py --all"
