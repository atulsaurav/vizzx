# VizzX

Reusable interactive DAG visualization frontend for Python web apps. Mount it in any FastAPI project, register your own API endpoints that return graph JSON, and get an interactive browser-based graph viewer with zoom, pan, collapse, highlight, minimap, and dark mode — out of the box.

Built on [d3 v5](https://d3js.org/) and [dagre-d3 v0.6.4](https://github.com/dagrejs/dagre-d3) (vendored, works offline).

## Installation

```bash
pip install vizzx
```

## Quick start

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from vizzx import create_ui_router, mount_static

app = FastAPI()

# Mount the interactive frontend
app.include_router(create_ui_router(
    title="My Graph Viewer",
    upload_accept=".zip,.json",
    upload_label="Upload a file to visualize",
))
mount_static(app)

# Implement your own analysis endpoint
@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    graph = my_analyzer(file)  # → {nodes, edges, modules}
    return JSONResponse(content=graph)
```

Then run with uvicorn:

```bash
uvicorn myapp:app --reload
```

## API

### `create_ui_router(**kwargs) → APIRouter`

Returns a FastAPI `APIRouter` that serves the interactive frontend at `GET /`.

| Parameter | Default | Description |
|---|---|---|
| `api_prefix` | `""` | URL prefix prepended to `/api/analyze` and `/api/preloaded` fetch calls |
| `title` | `"Graph Viewer"` | Browser tab title and page header |
| `upload_accept` | `""` | Comma-separated file extensions (e.g. `".zip,.csv"`). Empty = accept any file |
| `upload_label` | `"Upload a file to analyze"` | Text shown in the upload drop zone |

### `mount_static(app: FastAPI) → None`

Mounts the VizzX static assets (JS, CSS, vendor libraries) at `/static` on the given app.

## JSON contract

Your `/api/analyze` (and optionally `/api/preloaded`) endpoints must return JSON in this shape:

```json
{
  "nodes": [
    {
      "id": "unique.node.id",
      "label": "Display Name",
      "module": "group.name",
      "docstring": "Optional tooltip text",
      "external": false
    }
  ],
  "edges": [
    {
      "source": "caller.node.id",
      "target": "callee.node.id",
      "count": 1
    }
  ],
  "modules": {
    "group.name": ["unique.node.id", "another.node.id"]
  }
}
```

| Field | Required | Description |
|---|---|---|
| `nodes[].id` | Yes | Unique identifier for the node |
| `nodes[].label` | Yes | Display name shown in the graph |
| `nodes[].module` | Yes | Group/cluster the node belongs to. Dotted names create nested clusters |
| `nodes[].docstring` | No | Tooltip text shown on hover |
| `nodes[].external` | No | If `true`, node is rendered with dashed border (dimmed style) |
| `edges[].source` | Yes | Source node ID |
| `edges[].target` | Yes | Target node ID |
| `edges[].count` | No | Edge multiplicity (shown as label when > 1) |
| `modules` | Yes | Map of group name → list of node IDs in that group |

### Hierarchical clustering

The `module` field supports dotted names for nested clusters. For example, nodes with `module: "api.routes"` and `module: "api.models"` will be grouped under an `api` parent cluster automatically.

## Features

- **Zoom & pan** — mouse wheel zoom, click-drag to pan
- **Fit to screen** — toolbar button to auto-fit the graph
- **Node collapse** — double-click a node to hide all its downstream descendants
- **Highlight** — single-click to highlight direct callers/callees; toggle "Deep trace" for full upstream/downstream chains
- **Module view** — toggle between node-level and group-level views
- **Minimap** — SVG mode for small graphs, canvas mode for large ones
- **Dark mode** — toggle with persistent preference
- **Drag nodes** — reposition individual nodes with edges following

## Use cases

VizzX is designed to be the frontend for any tool that produces directed graphs:

- **Python call trees** — [VizzPy](https://github.com/atulsaurav/vizzpy) uses VizzX to visualize function call relationships
- **Class inheritance hierarchies** — map class → parent relationships
- **SQL dependency graphs** — visualize table/view dependencies
- **Build dependency graphs** — show module or package dependencies
- **Any DAG** — if you can express it as nodes, edges, and groups, VizzX can render it

## License

Apache-2.0