# Technical Preview PT-BR

Este exemplo sintético demonstra a interface local sem rede, credenciais, TMS ou provider vivo.
Ele preserva identificadores como `GET /orders/{order_id}`, `order_id` e `PENDING`, inclui casos
prontos/bloqueados, rastreabilidade e um conflito H4 sem vencedor inventado.

Na raiz do repositório, com o ambiente local instalado:

```powershell
.\.venv\Scripts\python.exe -m tools.build_technical_preview
Start-Process .\examples\technical-preview\output\test-plan.html
```

O primeiro comando reconstrói e valida deterministicamente o Project Model, a análise M2, o
relatório M3, o contexto de revisão e as relações H4 antes de escrever os artefatos. O HTML é
autocontido e pode ser aberto por duplo clique. O diretório `output/` é reproduzível e não é
versionado.

Também é possível rerenderizar o artefato canônico:

```powershell
.\.venv\Scripts\qe.exe render `
  .\examples\technical-preview\output\m3-generation-report.json `
  --review-context .\examples\technical-preview\output\review-context.json `
  --project-locale pt-BR --output-language pt-BR `
  --format html,markdown,json --output-dir .\examples\technical-preview\output\rerender
```

Limite honesto: H5 ainda não existe; portanto este D1 demonstra o renderer e o pipeline já
estruturado, não promete extrair semântica arbitrária diretamente de qualquer PRD em linguagem
natural. A fixture usa exclusivamente dados sintéticos genéricos do repositório.
