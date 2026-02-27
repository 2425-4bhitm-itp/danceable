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
        Log.info("Do not use InitBean in prod!!!");

        danceRepository.persist(
                new Dance(
                        "Chacha",
                        120,
                        128,
                        """
                                A lively Latin partner dance with syncopated “cha-cha-cha” steps, playful hip motion, and rhythm that breaks on the 4th and 1st beats.
                                """
                ),
                new Dance(
                        "Discofox",
                        112,
                        120,
                        """
                                A versatile social partner dance from the disco era, combining simple forward-and-back or side steps with turns and wraps; danced to 4/4 music and easy to pick up by beginners.
                                """
                ),
                new Dance(
                        "Jive",
                        168,
                        184,
                        """
                                A fast, energetic swing-influenced dance with quick rock-step and triple-step (shuffle) footwork, often danced to upbeat music in social and competitive settings.
                                """
                ),
                new Dance(
                        "Quickstep",
                        200,
                        208,
                        """
                                A brisk, flowing ballroom dance evolved from foxtrot, featuring running steps, syncopations, and light hops; danced in a smooth style with continuous forward movement.
                                """
                ),
                new Dance(
                        "Tango",
                        200,
                        208,
                        """
                                A dramatic ballroom dance with sharp, staccato movements and purposeful pauses, expressing strong character and musical accents.
                                """
                ),
                new Dance(
                        "Rumba",
                        100,
                        108,
                        """
                                A slow, sensual Latin ballroom dance emphasizing hip action and romantic connection, with smooth, deliberate steps and steady rhythm.
                                """
                ),
                new Dance(
                        "Salsa",
                        180,
                        300,
                        """
                                A popular Latin partner dance with energetic footwork, rhythmically syncopated timing, spins, and dynamic lead-follow patterns; danced in clubs worldwide.
                                """
                ),
                new Dance(
                        "Samba",
                        96,
                        104,
                        """
                                A rhythmic Latin dance from Brazil with a distinctive bounce action and forward-backward steps, often seen in both social and competitive dance scenes.
                                """
                ),
                new Dance(
                        "Slowwaltz",
                        84,
                        90,
                        """
                                A graceful ballroom dance in 3/4 time with smooth, flowing rise-and-fall movements and elegant progress around the floor.
                                """
                ),
                new Dance(
                        "Viennawaltz",
                        174,
                        180,
                        """
                                A fast, rotating form of waltz in 3/4 time with continuous turns and sweeping movement around the floor; one of the oldest ballroom dances.
                                """
                )
        );
    }
}
