# SearXNG MCP Server Usage Guide

A comprehensive guide for using the Enhanced SearXNG MCP Server v2.0.0 with full API parameter support.

## 🔍 **Overview**

The SearXNG MCP Server provides powerful metasearch capabilities through 5 specialized search tools, each supporting extensive customization through SearXNG's API parameters.

## 🛠️ **Available Search Tools**

### 1. `mcp_searxng_search` - General Web Search
### 2. `mcp_searxng_search_images` - Image Search  
### 3. `mcp_searxng_search_news` - News Search
### 4. `mcp_searxng_search_videos` - Video Search
### 5. `mcp_searxng_search_science` - Scientific Paper Search

---

## 📋 **Parameter Reference**

### **Core Parameters**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `query` | string | ✅ | Search query | `"machine learning"` |
| `categories` | string | ❌ | Comma-separated categories | `"general,news"` |
| `engines` | string | ❌ | Specific engines to use | `"google,bing,duckduckgo"` |
| `language` | string | ❌ | Search language code | `"en"`, `"fr"`, `"de"` |

### **Pagination & Filtering**

| Parameter | Type | Default | Description | Options |
|-----------|------|---------|-------------|---------|
| `pageno` | integer | 1 | Page number | `1`, `2`, `3`... |
| `time_range` | string | - | Time filter | `"day"`, `"month"`, `"year"` |
| `safesearch` | integer | 0 | Content filtering | `0` (off), `1` (moderate), `2` (strict) |
| `max_results` | integer | 10 | Result limit | `1-100` |

### **Output & Display**

| Parameter | Type | Default | Description | Options |
|-----------|------|---------|-------------|---------|
| `format` | string | "json" | Response format | `"json"`, `"csv"`, `"rss"` |
| `results_on_new_tab` | integer | 0 | UI preference | `0` (no), `1` (yes) |
| `image_proxy` | boolean | - | Proxy images | `true`, `false` |
| `autocomplete` | string | - | Autocomplete service | `"google"`, `"duckduckgo"`, `"wikipedia"` |

### **Advanced Control**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `enabled_plugins` | array | Enable specific plugins | `["Hash_plugin", "Tracker_URL_remover"]` |
| `disabled_plugins` | array | Disable specific plugins | `["Vim-like_hotkeys"]` |
| `enabled_engines` | array | Enable only these engines | `["google", "bing"]` |
| `disabled_engines` | array | Disable these engines | `["yandex"]` |

---

## 🎯 **Search Categories**

| Category | Description | Best For |
|----------|-------------|----------|
| `general` | Web pages, articles | General information |
| `images` | Pictures, photos | Visual content |
| `videos` | Video content | Tutorials, entertainment |
| `news` | News articles | Current events |
| `music` | Audio content | Songs, podcasts |
| `files` | Documents, PDFs | Research materials |
| `it` | Technical content | Programming, tech |
| `science` | Academic papers | Research, studies |
| `social media` | Social platforms | Trending topics |

---

## 🔧 **Usage Examples**

### **Basic Web Search**
```json
{
  "query": "climate change solutions",
  "max_results": 15
}
```

### **Advanced Web Search**
```json
{
  "query": "artificial intelligence ethics",
  "categories": "general,science",
  "engines": "google,bing,duckduckgo",
  "language": "en",
  "time_range": "month",
  "safesearch": 1,
  "max_results": 20
}
```

### **News Search with Time Filter**
```json
{
  "query": "renewable energy breakthrough",
  "time_range": "day",
  "engines": "reuters,bbc,cnn",
  "max_results": 10
}
```

### **Academic Research Search**
```json
{
  "query": "quantum computing algorithms",
  "engines": "arxiv,pubmed,google_scholar",
  "time_range": "year",
  "max_results": 15
}
```

### **Image Search with Specific Engines**
```json
{
  "query": "renewable energy infographics",
  "engines": "google_images,bing_images",
  "safesearch": 1,
  "image_proxy": true,
  "max_results": 12
}
```

### **Video Search for Tutorials**
```json
{
  "query": "machine learning tutorial",
  "engines": "youtube,vimeo",
  "time_range": "month",
  "max_results": 8
}
```

---

## 🎨 **Search Strategies**

### **For General Research**
- Use `categories: "general,science"` for comprehensive coverage
- Set `time_range: "year"` for recent, relevant content  
- Use `safesearch: 1` for filtered results

### **For News & Current Events**
- Use `mcp_searxng_search_news` tool
- Set `time_range: "day"` or `"month"`
- Specify news engines: `"reuters,bbc,cnn,ap"`

### **For Academic Research**
- Use `mcp_searxng_search_science` tool
- Include academic engines: `"arxiv,pubmed,google_scholar"`
- Use specific scientific terms in query

### **For Visual Content**
- Use `mcp_searxng_search_images` tool
- Enable `image_proxy: true` for privacy
- Use descriptive keywords

### **For Learning & Tutorials**
- Use `mcp_searxng_search_videos` tool
- Include "tutorial", "how to", "guide" in queries
- Specify `engines: "youtube,vimeo"`

---

## 🚀 **Advanced Features**

### **Plugin Control**
```json
{
  "query": "privacy search",
  "enabled_plugins": ["Tracker_URL_remover", "Ahmia_blacklist"],
  "disabled_plugins": ["Hostnames_plugin"]
}
```

### **Engine Management**
```json
{
  "query": "tech news",
  "enabled_engines": ["google", "bing", "duckduckgo"],
  "disabled_engines": ["yandex", "baidu"]
}
```

### **Multiple Output Formats**
```json
{
  "query": "data export",
  "format": "csv",
  "max_results": 50
}
```

---

## 💡 **Best Practices**

### **Query Optimization**
- ✅ Use specific, descriptive terms
- ✅ Include relevant keywords
- ✅ Use quotes for exact phrases: `"machine learning"`
- ✅ Use site-specific searches: `site:github.com python`

### **Parameter Selection**
- ✅ Match `time_range` to content freshness needs
- ✅ Use appropriate `safesearch` levels
- ✅ Select relevant `categories`
- ✅ Choose engines based on content type

### **Result Management**
- ✅ Set reasonable `max_results` (10-20 for most cases)
- ✅ Use pagination (`pageno`) for more results
- ✅ Consider `format` based on downstream processing

---

## 🔒 **Privacy & Safety**

### **Safe Search Levels**
- `0` - No filtering (adult content may appear)
- `1` - Moderate filtering (recommended for general use)  
- `2` - Strict filtering (family-safe content only)

### **Privacy Features**
- Use `image_proxy: true` to proxy images through SearXNG
- Enable `Tracker_URL_remover` plugin
- Avoid engines with heavy tracking if privacy is a concern

---

## 🎯 **Tool Selection Guide**

| Use Case | Recommended Tool | Key Parameters |
|----------|------------------|----------------|
| General research | `mcp_searxng_search` | `categories`, `time_range` |
| Current events | `mcp_searxng_search_news` | `time_range: "day"` |
| Visual content | `mcp_searxng_search_images` | `image_proxy`, `safesearch` |
| Learning materials | `mcp_searxng_search_videos` | `engines: "youtube"` |
| Academic research | `mcp_searxng_search_science` | `engines: "arxiv,pubmed"` |

---

## 🔍 **Popular Engine Combinations**

### **Comprehensive Web Search**
`"google,bing,duckduckgo,startpage"`

### **News Sources**
`"reuters,bbc,cnn,ap,guardian"`

### **Academic Sources**  
`"arxiv,pubmed,google_scholar,semantic_scholar"`

### **Image Sources**
`"google_images,bing_images,flickr"`

### **Video Sources**
`"youtube,vimeo,dailymotion"`

---

## 📊 **Response Format**

All searches return formatted markdown with:
- **Search metadata** (total results, engines used)
- **Numbered results** with titles and URLs
- **Content summaries** (up to 300 characters)
- **Additional fields** based on content type:
  - News: Publication date
  - Images: Thumbnails, formats
  - Videos: Duration
  - Science: DOI, authors
  - Source engine information

---

## 🚨 **Error Handling**

The MCP server handles various error conditions:
- Network connectivity issues
- Invalid parameters
- No results found
- JSON parsing errors
- Rate limiting

Always check response for error messages and adjust parameters accordingly.

---

## 📝 **Quick Reference Card**

```json
// Minimal search
{"query": "search term"}

// Comprehensive search  
{
  "query": "search term",
  "categories": "general,news",
  "engines": "google,bing",
  "language": "en",
  "time_range": "month",
  "safesearch": 1,
  "max_results": 15
}
```

---

*This guide covers SearXNG MCP Server v2.0.0 with full API parameter support. For technical issues, check server logs and ensure your SearXNG instance is accessible.* 