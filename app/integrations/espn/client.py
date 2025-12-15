from espn_api.football import League


class EspnClient:
    def get_league(
        self,
        *,
        league_id: str,
        year: int,
        espn_s2: str | None = None,
        swid: str | None = None,
    ) -> League:
        return League(
            league_id=league_id,
            year=year,
            espn_s2=espn_s2,
            swid=swid,
        )
