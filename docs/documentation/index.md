---
title: Documentation
hide:
- navigation
---

# Documentation

This document provides an overview of how documentation is structured, written, and deployed for this project.

This project uses [MkDocs](https://github.com/mkdocs/mkdocs) with the [mkdocstrings](https://github.com/mkdocstrings/mkdocstrings?tab=coc-ov-file) plugin to build a full documentation website from your Markdown files and Python docstrings. The main configuration for the site is stored in the `mkdocs.yml` file in the project root.

## Structure
The `docs/` directory contains the source files for your documentation website.
- `index.md`: This is the homepage of your documentation site. You should edit this file to provide a general introduction to your project.
- `reference.md`: This file is used to generate the API reference. The `::: your_project_name` marker inside it is automatically replaced by `mkdocstrings` with the documentation generated from your code's docstrings.

## Writing Documentation
### Docstring Format
The recommended format for docstrings is the **Google Python Style Guide**. Use sections like `Args`:, `Returns`:, and `Raises`: to ensure your docstrings are parsed correctly.

Here is an example of a well-documented function:
```python
def connect_to_api(api_key: str, endpoint: str, timeout: int = 10) -> dict:
    """Connects to an API endpoint and returns the JSON response.

    This function attempts to establish a connection to a given API
    endpoint using the provided API key.

    Args:
        api_key (str): The authentication key for the API.
        endpoint (str): The full URL of the API endpoint to connect to.
        timeout (int, optional): The connection timeout in seconds.
            Defaults to 10.

    Returns:
        dict: A dictionary containing the JSON response from the API.

    Raises:
        ValueError: If the API key is empty or the endpoint is invalid.
        ConnectionError: If a connection cannot be established.
    """
    # function implementation...
```

### Viewing Docs Locally
To preview your documentation website as you make changes, run the following command from the project root:
```bash
mkdocs serve
```

This will start a local web server, and you can view your site at `http://127.0.0.1:8000`. The site will automatically reload when you save changes.

## Deployment to GitHub Pages
The workflow in `.github/workflows/docs.yml` automatically builds and deploys your documentation website.

> [!NOTE]
> To enable the workflow, add the `.yml` file extension to the workflow file.

For this to work, you must perform a **one-time setup** in your repository settings:
1. Navigate to your repository's **Settings** tab.
2. Go to the **Pages** section in the left sidebar.
3. Under **Build and deployment**, set the **Source** to **GitHub Actions**.

After this is configured, any push to the `main` branch will trigger the workflow and update your live documentation site.

### Using Custom Domain
To use a custom domain (e.g., `www.your-project.com`) for your documentation site:

#### Configure Your DNS Provider
1. Log in to your domain registrar (e.g., GoDaddy, Namecheap).
2. Create a `CNAME` record for your **subdomain** that points to `<your-username>.github.io`.

#### Configure GitHub
1. In your repository, go to **Settings** > **Pages**.
2. Under **Custom domain**, enter your full domain (e.g., `www.your-project.com`) and click **Save**.
3. Once the domain is verified, check the **Enforce HTTPS** box.
