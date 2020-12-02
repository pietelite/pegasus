class NosqlHandlerInterface:

    def insert_video_config(self, video_id: str, config: dict) -> None:
        raise NotImplementedError

    def get_video_config(self, video_id: str) -> dict:
        raise NotImplementedError

    def delete_video_config(self, video_id: str) -> None:
        raise NotImplementedError
