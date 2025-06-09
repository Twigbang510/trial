import { useEffect, useState } from "react";
import { Howl } from "howler";

const useAudioPlayer = () => {
  const [currentSound, setCurrentSound] = useState<Howl | null>(null);

  useEffect(() => {
    Howler.autoUnlock = true;
  }, []);

  const play = (url: string) => {
    if (currentSound) {
      currentSound.stop();
    }

    const sound = new Howl({
      src: [url],
      html5: true,
      onplay: () => {
        console.log("Playing audio:", url);
      },
      onend: () => {
        setCurrentSound(null);
      },
      onplayerror: () => {
        sound.once("unlock", () => sound.play());
      },
    });

    sound.play();
    setCurrentSound(sound);
  };

  const stop = () => {
    currentSound?.stop();
    setCurrentSound(null);
  };

  return { play, stop };
};

export default useAudioPlayer;
