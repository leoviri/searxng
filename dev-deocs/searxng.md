markdown
# SearXNG Developer Documentation

This document provides guidance for developers looking to contribute to SearXNG, understand its codebase, or develop new features like engines and plugins.

**Source:** This documentation is based on the official SearXNG developer guide: [https://docs.searxng.org/dev/index.html](https://docs.searxng.org/dev/index.html)

## 1. Introduction

SearXNG is a free internet metasearch engine which aggregates results from more than 70 search services. Users are neither tracked nor profiled. Additionally, SearXNG can be used over Tor for online anonymity.

This guide covers:
*   Setting up a development environment.
*   Understanding the code structure.
*   Developing engines and plugins.
*   Contributing to the project.

## 2. Development Environment Setup

### 2.1. Prerequisites

Before you start, ensure you have the following installed:
*   **Git:** For version control.
*   **Python:** Version 3.8 or higher.
*   **pip:** Python package installer.
*   **virtualenv:** (Recommended) To create isolated Python environments.
*   **Node.js & npm:** (Optional, for frontend development) For managing JavaScript dependencies and building frontend assets.

### 2.2. Getting the Code

Clone the SearXNG repository from GitHub:
```bash
git clone https://github.com/searxng/searxng.git
cd searxng
```

### 2.3. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment (e.g., named 'venv')
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (Git Bash or WSL):
source venv/Scripts/activate
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```
You should see `(venv)` prefixed to your shell prompt.

### 2.4. Install Dependencies

Install the required Python dependencies:

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (for testing, linting, etc.)
pip install -e .[dev]
```
If you plan to work on the frontend (CSS/JS), install Node.js dependencies:
```bash
npm install
```

### 2.5. Initial Configuration

SearXNG uses a `settings.yml` file for configuration. A template is provided as `searx/settings.yml.template`.

1.  Copy the template:
    ```bash
    cp searx/settings.yml.template searx/settings.yml
    ```
2.  **Generate a secret key:**
    Open `searx/settings.yml` and find the `secret_key` setting. You need to replace `"ultrasecretkey"` with a long, random string. You can generate one using:
    ```bash
    openssl rand -hex 32
    ```
    Paste this generated key into your `settings.yml`.
3.  (Optional) Enable `debug: true` in `searx/settings.yml` for development. This provides more verbose output and enables live reloading.

### 2.6. Running SearXNG for Development

Once dependencies are installed and `settings.yml` is configured, you can run the development server:

```bash
python searx/webapp.py
```
By default, SearXNG will be accessible at `http://127.0.0.1:8080/`.

If you made changes to frontend assets (SCSS, JS), you might need to rebuild them:
```bash
npm run build
```
During development with `debug: true`, some frontend changes might be picked up automatically, but a full rebuild is sometimes necessary.

## 3. Code Structure

SearXNG's codebase is primarily organized into:

*   **`searx/`**: The main Python package.
    *   **`searx/webapp.py`**: The entry point for running the Flask web application.
    *   **`searx/settings.yml.template`**: Template for instance configuration.
    *   **`searx/engines/`**: Contains the code for individual search engines. Each engine is a Python file.
    *   **`searx/plugins/`**: Contains the code for plugins that can modify requests or results.
    *   **`searx/search/`**: Core search logic, result parsing, and aggregation.
    *   **`searx/static/`**: Static assets (CSS, JavaScript, images).
        *   `searx/static/themes/`: Contains different themes.
        *   `searx/static/js/`: JavaScript files.
        *   `searx/static/css/`: CSS/SCSS files.
    *   **`searx/templates/`**: Jinja2 HTML templates used to render pages.
    *   **`searx/translations/`**: Localization files (`.po` files).
*   **`tests/`**: Contains unit and integration tests.
*   **`utils/`**: Utility scripts for development, deployment, and maintenance.
*   **`Dockerfile` / `docker-compose.yml`**: Files for Docker-based deployment.
*   **`package.json` / `package-lock.json`**: Node.js project and dependency files.
*   **`webpack.config.js`**: Webpack configuration for building frontend assets.

### Backend
The backend is built using Python and the Flask web framework. It handles:
*   User requests.
*   Querying enabled search engines.
*   Aggregating and parsing results.
*   Applying plugin modifications.
*   Rendering HTML templates.

### Frontend
The frontend uses:
*   **HTML**: Structured with Jinja2 templates.
*   **CSS**: Styled using SCSS, which is compiled to CSS.
*   **JavaScript**: For client-side interactions and enhancements.
Frontend assets are managed and built using `npm` and Webpack.

## 4. Working with Engines

Engines are the core of SearXNG, responsible for fetching results from various external search providers.

### 4.1. Adding a New Engine

1.  **Create a new Python file** in the `searx/engines/` directory (e.g., `mynewengine.py`).
2.  **Engine Structure:**
    Your engine will typically inherit from `searx.engines.xpath.XPathEngine` (if the source is HTML and can be parsed with XPath) or `searx.engines.json.JSONEngine` (if the source provides a JSON API). A basic structure:
    ```python
    # searx/engines/mynewengine.py
    from searx.engines.xpath import XPathEngine # or json.JSONEngine
    from searx.url_utils import urlencode

    # Engine metadata
    categories = ['general', 'custom'] # Example categories
    paging = True # Does the engine support pagination?
    time_range_support = False # Does it support time range searches?
    # ... other metadata (see existing engines for examples)

    # Base URL for the search engine
    base_url = 'https://api.example.com/' # Or website URL
    search_url = base_url + 'search?q={query}&page={page}' # Example

    class MyNewEngine(XPathEngine): # Or JSONEngine
        def request(self, query, params):
            # Prepare the request URL and headers
            # `params['url']` will be search_url formatted with query and page
            # `params['headers']` can be modified
            # `params['method']` (GET/POST)
            # `params['data']` (for POST)
            # ...
            return params # Must return the modified params

        def response(self, resp):
            # Parse the response object `resp` (which is a `requests.Response` object)
            # Extract search results
            results = []
            # For XPathEngine, use self.xpath_results(resp.text, ...)
            # For JSONEngine, use self.json_results(resp.json(), ...)
            #
            # Each result should be a dictionary, e.g.:
            # results.append({
            #     'url': 'http://example.com/result1',
            #     'title': 'Example Result 1',
            #     'content': 'Description of the result.'
            # })
            return results # Must return a list of result dictionaries
    ```
3.  **Define XPath expressions (for XPathEngine):**
    If using `XPathEngine`, you'll need to define XPath selectors to extract data:
    ```python
    # ... inside MyNewEngine class or at module level
    # XPath selectors for results
    results_xpath = '//div[@class="result-item"]'
    url_xpath = './/a[@class="result-link"]/@href'
    title_xpath = './/h3[@class="result-title"]/text()'
    content_xpath = './/p[@class="result-description"]/text()'
    # ... other xpaths like suggestion_xpath, image_xpath, etc.
    ```
4.  **Implement `request(self, query, params)`:**
    This method prepares the search request. You can modify `params['url']`, `params['headers']`, etc.
5.  **Implement `response(self, resp)`:**
    This method parses the HTTP response (`resp`) from the external engine and extracts search results into a list of dictionaries. Each dictionary represents a search result and should contain keys like `url`, `title`, `content`.
6.  **Testing the Engine:**
    Use the `searx.search.Search` object or run SearXNG locally and enable your engine in `settings.yml` to test.
    Refer to `tests/unit/test_engine_*.py` for examples of engine unit tests.

### 4.2. Engine Configuration

Engines are configured in `searx/settings.yml` under the `engines:` section.
*   **Enable/Disable:** List engines you want to use.
*   **API Keys:** Some engines require API keys, which can be specified here.
*   **Engine-specific parameters:** Some engines might have specific settings.

Example from `settings.yml.template`:
```yaml
engines:
  # - name: wikipedia
  #   engine: wikipedia
  #   shortcut: wp
  #   categories:
  #     - general
  #     - science
  #   token: null  # no API key or an empty one (see also general.yml)
  #   timeout: 3.0
  #   disabled: false
  # - name: my new engine # This is how you would add your engine
  #   engine: mynewengine # Corresponds to mynewengine.py
  #   shortcut: mne
  #   categories: [custom]
```

### 4.3. Engine Best Practices

*   Respect `robots.txt` of the target sites (SearXNG does this by default).
*   Handle rate limits and errors gracefully.
*   Set appropriate User-Agent strings if necessary.
*   Provide comprehensive tests for your engine.
*   Follow the coding style of existing engines.

## 5. Working with Plugins

Plugins allow modification of SearXNG's behavior at various stages of the search process. They can:
*   Modify search queries.
*   Filter or transform search results.
*   Add new functionality.

### 5.1. Creating a Plugin

1.  Create a new Python file in `searx/plugins/` (e.g., `myplugin.py`).
2.  Define a plugin class and implement one or more hook methods. Available hooks include:
    *   `on_search_request(request, search_query)`
    *   `on_search_response(request, search_query, results)`
    *   `on_result_item(result, search_query)`
    *   And others (see `searx/plugins/__init__.py` or existing plugins).

    Example:
    ```python
    # searx/plugins/myplugin.py
    from searx.plugins import SimplePlugin

    class MyCustomPlugin(SimplePlugin):
        def on_result_item(self, result, search_query):
            # Example: Add a prefix to all result titles
            if 'title' in result:
                result['title'] = "[MyPlugin] " + result['title']
            return result # Must return the modified result or None to filter it
    ```
3.  **Enable the Plugin:** Add your plugin to the `plugins:` list in `searx/settings.yml`:
    ```yaml
    plugins:
      - name: myplugin # Corresponds to myplugin.py
        # Optional plugin-specific settings can go here
        # my_setting: value
    ```

## 6. Internationalization (i18n) / Translations

SearXNG supports multiple languages through Gettext (`.po` files).
*   Translation files are located in `searx/translations/<lang_code>/LC_MESSAGES/messages.po`.
*   To update or add translations:
    1.  Extract translatable strings from the source code:
        ```bash
        pybabel extract -F babel.cfg -o searx/messages.pot ./searx
        ```
    2.  Update existing `.po` files for each language:
        ```bash
        pybabel update -i searx/messages.pot -d searx/translations
        ```
    3.  If adding a new language (e.g., `xx`):
        ```bash
        pybabel init -i searx/messages.pot -d searx/translations -l xx
        ```
    4.  Translate the strings in the `<lang_code>/LC_MESSAGES/messages.po` file using a PO editor (like Poedit) or a text editor.
    5.  Compile the translations:
        ```bash
        pybabel compile -d searx/translations
        ```

## 7. Testing

SearXNG uses `pytest` for testing.
*   Tests are located in the `tests/` directory.
*   To run all tests:
    ```bash
    pytest
    ```
*   To run specific tests:
    ```bash
    pytest tests/unit/test_some_module.py
    pytest tests/unit/test_some_module.py::TestClass::test_method
    ```
*   New code contributions should ideally include relevant tests.

## 8. API

SearXNG provides a search API that returns results in various formats (JSON, CSV, RSS). The API largely mirrors the parameters available in the web interface.
*   **Documentation:** The API is described in detail in the [SearXNG API Documentation](https://docs.searxng.org/user/API.html).
*   **Endpoint:** Typically `http://your-searxng-instance/search`
*   **Parameters:** `q` (query), `format` (json, csv, rss), `categories`, `engines`, `pageno`, etc.

Example API call for JSON results:
`http://127.0.0.1:8080/search?q=searxng&format=json&categories=general`

## 9. Contributing

Contributions to SearXNG are welcome!

### 9.1. Code Style and Linting

*   SearXNG uses **Black** for Python code formatting and **Flake8** for linting.
*   Ensure your code adheres to these standards. You can run them locally:
    ```bash
    black .
    flake8 .
    ```
*   For frontend code (JS/CSS), Prettier might be used. Check `package.json` for linting/formatting scripts.

### 9.2. Pull Requests (PRs)

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix: `git checkout -b my-feature-branch`.
3.  **Make your changes** and commit them with clear, descriptive messages.
4.  **Add tests** for new functionality or bug fixes.
5.  **Ensure all tests pass** (`pytest`).
6.  **Ensure code is linted and formatted** (`black .`, `flake8 .`).
7.  **Push your branch** to your fork: `git push origin my-feature-branch`.
8.  **Open a Pull Request** against the `master` branch of the `searxng/searxng` repository.
9.  Provide a clear description of your changes in the PR.
10. Be responsive to feedback and review comments.

### 9.3. Reporting Issues

*   If you find a bug or have a feature request, please check existing issues first.
*   If not already reported, open a new issue on the [SearXNG GitHub Issues page](https://github.com/searxng/searxng/issues).
*   Provide as much detail as possible: SearXNG version, browser, steps to reproduce, expected behavior, actual behavior.

### 9.4. Communication

*   **Matrix:** The primary communication channel for developers and users is Matrix: [#searxng:matrix.org](https://matrix.to/#/#searxng:matrix.org).

## 10. License

SearXNG is licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**.
Ensure your contributions are compatible with this license.

---

This concludes the developer documentation overview. For more specific details, refer to the source code, existing engines/plugins, and the official documentation linked at the beginning. Happy coding!