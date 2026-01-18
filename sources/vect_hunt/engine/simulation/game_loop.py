import pygame


class GameLoop:
    """
    Boucle principale du jeu (fixed timestep + rendu).
    """

    def __init__(
        self,
        game,
        scheduler,
        clock: pygame.time.Clock,
        fps: int,
        sim_dt: float,
        logger,
        max_accumulator_multiplier: int = 4,
    ) -> None:
        """
        Initialise la boucle de jeu.

        Parameters
        ----------
        game : Game
            Instance du jeu à mettre à jour et rendre.
        scheduler : SimulationScheduler
            Orchestrateur de simulation (gère les événements et l'input).
        clock : pygame.time.Clock
            Horloge Pygame pour gérer le timing.
        fps : int
            Nombre maximal de frames par seconde.
        sim_dt : float
            Pas de temps fixe pour la simulation (en secondes).
        logger : Logger
            Logger pour les messages de la boucle de jeu.
        max_accumulator_multiplier : int
            Multiplicateur pour limiter l'accumulateur de temps.
        """
        self.game = game
        self.scheduler = scheduler
        self.clock = clock
        self.fps = fps
        self.sim_dt = sim_dt
        self.logger = logger
        self.max_accumulator_multiplier = max_accumulator_multiplier

        self._running = False
        self._accumulator = 0.0

    def run(self) -> None:
        """
        Démarre la boucle principale du jeu.
        """
        self._running = True
        while self._running:
            self._process_events()
            self._tick()

    def stop(self) -> None:
        """
        Arrête la boucle principale du jeu.
        """
        self._running = False

    def _process_events(self) -> None:
        """
        Traite les événements Pygame.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                continue
            self.scheduler.handle_event(event)

    def _tick(self) -> None:
        """
        Effectue une itération de la boucle de jeu.
        Gère la mise à jour de la simulation et le rendu.
        """
        frame_time = self.clock.tick(self.fps) / 1000.0
        self._accumulator += frame_time

        max_accumulator = self.sim_dt * self.max_accumulator_multiplier
        if self._accumulator > max_accumulator:
            self.logger.warning(
                "Temps d'execution trop long, limitation de l'accumulateur | "
                "accumulator=%f | frame_time=%f",
                self._accumulator,
                frame_time,
            )
            self._accumulator = max_accumulator

        while self._accumulator >= self.sim_dt:
            self.game.update(self.sim_dt)
            self._accumulator -= self.sim_dt

        self.game.render()
