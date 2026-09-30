from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_model_dir, get_store
from app.schemas.whatif import WhatIfRequest, WhatIfResponse
from app.services import whatif_service
from app.services.data_store import DataStore

router = APIRouter(prefix="/api/whatif", tags=["whatif"])


@router.post("/{race_id}", response_model=WhatIfResponse)
def whatif(
    race_id: str,
    request: WhatIfRequest,
    store: DataStore = Depends(get_store),
    model_dir: str = Depends(get_model_dir),
) -> WhatIfResponse:
    result = whatif_service.run_whatif(store, model_dir, race_id, request)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Could not build a what-if scenario for race '{race_id}'.")
    return result
