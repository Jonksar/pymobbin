# PyMobbin

A Python client library for the Mobbin API.

## Installation

```bash
uv pip install pymobbin
```

## Usage

```python
import asyncio
from pymobbin.client import MobbinClient

async def main():
    client = MobbinClient()
    # auth flow...
    # await client.send_email("user@example.com")
    # ...
```

