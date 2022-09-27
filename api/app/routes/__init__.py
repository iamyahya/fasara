from .gate import router as gate_router
from .user import router as user_router
from .system import router as system_router
from .topic import router as topic_router
from .hadith import router as hadith_router
from .quran import router as quran_router
from .response import router as response_router


routes = [
    gate_router,
    user_router,
    system_router,
    topic_router,
    hadith_router,
    quran_router,
    response_router
]
