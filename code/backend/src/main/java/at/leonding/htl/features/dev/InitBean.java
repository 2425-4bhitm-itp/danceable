package at.leonding.htl.features.dev;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
import io.quarkus.logging.Log;
import io.quarkus.runtime.LaunchMode;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;

@ApplicationScoped
public class InitBean {
    @Inject
    DanceRepository danceRepository;

    @Transactional
    void startup(@Observes StartupEvent startupEvent) {
        if (LaunchMode.current() == LaunchMode.NORMAL) {
            Log.info("Do not use InitBean in prod!!!");

            danceRepository.persist(
                    new Dance("Discofox", 112, 120),
                    new Dance("Slowwaltz", 84, 90),
                    new Dance("Viennawaltz", 174, 180),
                    new Dance("Chacha", 120, 128),
                    new Dance("Foxtrott", 112, 120),
                    new Dance("Quickstep", 200, 208),
                    new Dance("Salsa", 180, 300),
                    new Dance("Rumba", 100, 108),
                    new Dance("Samba", 96, 104),
                    new Dance("Jive", 168, 184)
            );
        }
    }
}
