import pytest
from app.models.analytics import Candidate, UserEvent
from app.schemas.analytics import UserEventCreate, CandidateUpdate
from pydantic import ValidationError

class TestAnalyticsEngineSafe:
    def test_schema_event_valid(self):
        schema = UserEventCreate(
            evento="video_play", 
            categoria="interaccion", 
            metadata_evento={"video_id": 5, "duration": 120}
        )
        assert schema.evento == "video_play"
        assert schema.metadata_evento["video_id"] == 5

    def test_schema_candidate_invalid_score(self):
        with pytest.raises(ValidationError):
            CandidateUpdate(puntuacion_total=150) # Score > 100
            
    def test_schema_candidate_negative_score(self):
        with pytest.raises(ValidationError):
            CandidateUpdate(puntuacion_total=-10)

    def test_model_candidate_init(self):
        cand = Candidate(
            empresa_id=1, 
            usuario_id=2, 
            origen="simulacion", 
            estado_candidato="nuevo", 
            contactado=False
        )
        assert cand.estado_candidato == "nuevo"
        assert cand.contactado is False

    def test_model_userevent_jsonb_handling(self):
        evt = UserEvent(
            evento="login", 
            categoria="auth", 
            metadata_evento={"ip": "127.0.0.1", "device": "mobile"}
        )
        assert evt.categoria == "auth"
        assert "device" in evt.metadata_evento
