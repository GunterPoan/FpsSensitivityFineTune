from dataclasses import dataclass

@dataclass
class R6Settings:
    """
    Store the data source from R6
    """

    dpi: int = 900
    fov: int = 84
    aspectRatio: str = "16:9"
    resolution: str = "1920x1080"
    horizontalSens: int = 10
    verticalSens: int = 10
    selectedAds: int = 0
    xfactorAiming: float = 0.00223
    threshold: int = 15