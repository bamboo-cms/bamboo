# Bamboo

A CMS optimized for conference hosting

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/bamboo-cms/bamboo/assets/16336606/7f276425-e39b-4c52-95ba-c226fa6dd156">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/bamboo-cms/bamboo/assets/16336606/363b9bb0-8b39-496a-9d83-ba76247a80f7">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="https://github.com/bamboo-cms/bamboo/assets/16336606/363b9bb0-8b39-496a-9d83-ba76247a80f7">
</picture>

## Development

Clone the repository:

```bash
git clone https://github.com/bamboo-cms/bamboo
cd bamboo
```

Make sure you have Python 3.12 and [PDM](https://pdm-project.org/) installed, then install the dependencies:

```bash
pdm install
```

Run the backend application:

```bash
pdm serve
```

You can create tables in the database by running:

```bash
pdm drop-tables
pdm create-tables
```

Lint backend

```bash
pdm run pre-commit run --all-files
```

> [!TIP]
> It's recommended to install the [pre-commit](https://pre-commit.com/) hook to automatically lint your code before committing:
> ```bash
> pdm run pre-commit install
> ```

Run the frontend development server (need to install [pnpm](https://pnpm.io/)):

```bash
cd frontend
pnpm install
pnpm dev
```

Lint frontend

```bash
pnpm run lint
```
