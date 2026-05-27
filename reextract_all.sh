#!/bin/bash
# Script para reextrair todas as palestras com o extrator melhorado

echo "Instalando dependências necessárias..."
pip3 install beautifulsoup4 markdownify --quiet 2>/dev/null || pip install beautifulsoup4 markdownify --quiet 2>/dev/null

echo ""
echo "Reextraindo todas as palestras com o extrator atualizado..."
python3 scripts/extract_transcript.py --all

echo ""
echo "Extração concluída!"
echo "Agora revise as traduções PT-BR das palestras que tiveram seções recuperadas."
