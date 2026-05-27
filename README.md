# Jordan Peterson — Biblical Stories (Transcrições Bilíngues)

Transcrições completas e de alta qualidade da série **"The Psychological Significance of the Biblical Stories"** (2017) de Jordan B. Peterson.

O projeto oferece as 16 palestras (15 principais + o bônus "On the Death and Resurrection") em:

- **Inglês** (original falado)
- **Português do Brasil** (tradução oral, fluida, pronta para uso)

## Estrutura

```
.
├── README.md
├── scripts/                    # Ferramentas reutilizáveis
│   ├── lectures.py             # Single source of truth (metadados das 16 lectures)
│   ├── extract_transcript.py
│   └── download_covers.py
└── Biblical Stories/
    ├── README.md               # Índice completo + diretrizes de tradução
    ├── EN/                     # 16 palestras em inglês
    └── PT-BR/                  # 16 palestras em português brasileiro
```

## Destaques da versão PT-BR

- Tom **oral brasileiro** (frases curtas, variação de vocabulário, contrações naturais).
- **Notas de rodapé** para termos técnicos, conceitos filosóficos, mitológicos e ambiguidades.
- **Paridade rigorosa**: todas as seções + timestamps literais `[TIMESTAMP](https://youtu.be/...)` replicados exatamente do original.
- Controle de qualidade com Lecture 01 como referência de estilo e fluidez.

## Como usar

1. Clone o repositório.
2. As transcrições estão em `Biblical Stories/PT-BR/` e `Biblical Stories/EN/`.
3. O arquivo `scripts/lectures.py` contém o mapeamento oficial de todas as 16 palestras (IDs do YouTube, títulos, etc.).

## Licença

As transcrições em inglês são baseadas nas palestras públicas de Jordan Peterson.  
A tradução para português brasileiro foi realizada com foco em fidelidade ao tom oral e utilidade para o público brasileiro.

## Contribuições

Melhorias na tradução, correções de fluidez ou novas notas de rodapé são bem-vindas via Pull Request.

## Ebooks Automatizados (EPUB / MOBI)

Este repositório gera automaticamente, via **GitHub Actions**, versões em ebook da edição completa (Omnibus) com todas as 16 palestras:

- **EPUB** (recomendado para a maioria dos leitores)
- **MOBI** (otimizado para Kindle)

> **PDF**: O PDF da edição omnibus **não é mais gerado automaticamente** no GitHub Actions.  
> Você pode gerá-lo localmente com:
> ```bash
> python3 scripts/generate_omnibus.py --lang en --pdf
> python3 scripts/generate_omnibus.py --lang pt --pdf
> ```

### Idiomas
- Inglês (EN)
- Português do Brasil (PT-BR)

### Tipos de Edições

**Edição Completa (Omnibus)**
- **Uma única versão** contendo **todas as 16 palestras** juntas
- Ideal para referência, busca de termos ou leitura sequencial completa da série
- Cada edição inclui agora uma introdução e metadados claros de origem (incluindo link para este repositório)
- Arquivos nomeados como:
  - `Jordan Peterson - Biblical Stories - EN.epub`
  - `Jordan Peterson - Histórias Bíblicas - PT-BR.epub`

### Como baixar

Os arquivos estão disponíveis em **GitHub Releases** (a forma mais habitual e recomendada):

1. Vá em **[Releases](https://github.com/thiagodamas/jordan-peterson-biblical-stories/releases)**
2. Baixe a versão mais recente (`ebooks-XXXX`)

Os nomes dos arquivos são limpos (sem espaços) para facilitar o download:

- `Jordan-Peterson-Biblical-Stories-EN.epub`
- `Jordan-Peterson-Biblical-Stories-EN.mobi`
- `Jordan-Peterson-Historias-Biblicas-PT-BR.epub`
- `Jordan-Peterson-Historias-Biblicas-PT-BR.mobi`

### Gatilhos
- Todo push na branch `main` que modifica as transcrições dispara uma nova build.
- Você também pode acionar manualmente em **Actions → Build Ebooks**.

---

**Repositório original**: https://github.com/thiagodamas/jordan-peterson-biblical-stories
