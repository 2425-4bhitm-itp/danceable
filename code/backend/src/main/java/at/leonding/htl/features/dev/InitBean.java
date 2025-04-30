package at.leonding.htl.features.dev;

import at.leonding.htl.features.library.dance.Dance;
import at.leonding.htl.features.library.dance.DanceRepository;
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
            System.out.println("InitBean.startup");

            danceRepository.persist(
                    new Dance("Slow Waltz", 84, 90),
                    new Dance("Viennese Waltz", 174, 180),
                    new Dance("Foxtrott", 112, 120),
                    new Dance("Quickstep", 200, 208),
                    new Dance("Tango", 120, 140),
                    new Dance("Cha Cha Cha", 120, 128),
                    new Dance("Rumba", 100, 108),
                    new Dance("Samba", 96, 104),
                    new Dance("Jive", 168, 184),
                    new Dance("Blues Dance", 20, 75),
                    new Dance("Tango Argentino", 80, 160),
                    new Dance("Salsa", 180, 300),
                    new Dance("Bachata", 90, 200)
            );
        }
    }
}
