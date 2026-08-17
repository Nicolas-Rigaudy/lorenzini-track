import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

router = APIRouter(prefix="/tiles", tags=["tiles"])

# EMODnet Bathymetry has no CORS headers, so browsers can't fetch its tiles
# directly from a different origin. We proxy them server-side instead.
#
# "baselayer" is the layer with genuine global coverage (WGS84 bbox -180/-90 to 180/90,
# per https://tiles.emodnet-bathymetry.eu/wmts/1.0.0/WMTSCapabilities.xml). The similarly-named
# "mean_atlas_land"/"mean_atlas_land_latest" etc. layers are NOT global - they're restricted to
# roughly -70.5/11 to 43/90 (Atlantic/European waters) and return 500s for out-of-bounds tiles.
BATHYMETRY_UPSTREAM = "https://tiles.emodnet-bathymetry.eu/2020/baselayer/web_mercator"

# Reused across requests (not created per-request) to avoid a new TLS handshake per tile.
_client = httpx.AsyncClient(timeout=10.0)


@router.get("/bathymetry/{z}/{x}/{y}.png")
async def bathymetry_tile(z: int, x: int, y: int) -> Response:
    url = f"{BATHYMETRY_UPSTREAM}/{z}/{x}/{y}.png"
    upstream_response = await _client.get(url)

    if upstream_response.status_code != 200:
        raise HTTPException(status_code=upstream_response.status_code)

    return Response(content=upstream_response.content, media_type="image/png")
