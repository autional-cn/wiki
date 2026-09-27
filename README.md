# Autional API Wiki Portal

**Domain**: wiki.autional.cn
**Stack**: Astro 5 + Tailwind 3.4
**Repository**: [github.com/autional-cn/wiki](https://github.com/autional-cn/wiki)

## Development

```bash
pnpm install
pnpm dev      # http://localhost:4435
pnpm build    # Static output to dist/
```

## Content Source

Chinese Wiki HTML synced from the AuthMS backend monorepo:
`D:\go\auth_ms_new\document\generated\wiki\html\` → `public/wiki/api/`

## Update Content

```bash
cd D:\go\auth_ms_new
python scripts/generate/generate_api_wiki.py --html   # generate Chinese HTML
python D:\ws\autional-cn\sites\wiki\scripts\sync-wiki-zh.py   # sync + normalize for .cn
pnpm build                                            # rebuild
```
