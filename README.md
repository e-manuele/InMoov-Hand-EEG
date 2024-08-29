# Arduino control for InMoov hand.
- Serial monitor
- Neurosky Mindwave

Project InMoov: http://inmoov.fr  (Gael Langevin)

## Important
Please check this repositories for information related to using Neurosky Mindwave Mobile headsets with Arduino boards:
- https://github.com/ailr16/NeuroSkyMindwave-Arduino
- https://github.com/ailr16/mindwave-arduino-tools

The last one (mindwave-arduino-tools) is work in progress, so I'll give support for some months and any related questions and contributions are welcome

## Media
Some videos using Neurosky Mindwave:
- https://www.youtube.com/watch?v=0HPReJuST-8
- https://youtu.be/T_Hp-smvf4k?si=S2atUgjazWCHk9-4
- https://youtu.be/9V0qPo44Z9E?si=oWs4hMWysrngGh9-
- https://youtu.be/uKK5_U6l27E?si=hh_cAgwqUVtbNMUl
- https://youtu.be/0bHTYiXq0eg?si=vZIBMIrzV8-c2v0V
- https://youtu.be/Gy3pmSiWoW0?si=KFM5Ls6BB6W91R6V

Il codice che hai fornito è per un braccio robotico comandato tramite un'interfaccia Bluetooth che riceve dati da un EEG NeuroSky. La struttura principale del codice riguarda la lettura e l'interpretazione dei dati seriali provenienti dal dispositivo NeuroSky attraverso Bluetooth. Vediamo come il codice gestisce questi dati:

### 1. Lettura dei dati seriali

La funzione `ReadOneByte()` è utilizzata per leggere un byte alla volta dal buffer seriale:

```cpp
byte ReadOneByte() {
  int ByteRead;
  while(!Serial.available());
  ByteRead = Serial.read();
  return ByteRead;
}
```

### 2. Individuazione del pacchetto di dati

Il codice cerca due byte di sincronizzazione (170 o 0xAA) per iniziare a leggere un pacchetto di dati:

```cpp
if(ReadOneByte() == 170) {
  if(ReadOneByte() == 170) {
    // Lettura della lunghezza del payload
    payloadLength = ReadOneByte();
    if(payloadLength > 169) return;
    
    // Lettura del payload
    generatedChecksum = 0;
    for(int i = 0; i < payloadLength; i++) {
      payloadData[i] = ReadOneByte();
      generatedChecksum += payloadData[i];
    }
    
    // Lettura del checksum
    checksum = ReadOneByte();
    generatedChecksum = 255 - generatedChecksum;

    if(checksum == generatedChecksum) {
      // Interpretazione del payload
    }
  }
}
```

### 3. Interpretazione del payload

Il payload contiene vari byte che rappresentano diversi tipi di dati. Il codice li interpreta tramite un ciclo `for` e uno `switch`:

```cpp
for(int i = 0; i < payloadLength; i++) {
  switch (payloadData[i]) {
    case 2:
      i++;
      poorQuality = payloadData[i];
      bigPacket = true;
      break;
    case 4:
      i++;
      attention = payloadData[i];
      break;
    case 5:
      i++;
      meditation = payloadData[i];
      break;
    case 0x80:
      i = i + 3;
      break;
    case 0x83:
      i = i + 25;
      break;
    default:
      break;
  }
}
```

### 4. Utilizzo dei dati

Una volta che i dati sono stati interpretati, vengono utilizzati per controllare i servomotori del braccio robotico. L'esempio utilizza il valore di `attention` per determinare la posizione dei servomotori:

```cpp
if(bigPacket) {
  if(poorQuality == 0)
    digitalWrite(LED, HIGH);
  else
    digitalWrite(LED, LOW);

  switch(attention / 10) {
    case 0:
      menique.write(meniqueH);
      anular.write(anularH);
      medio.write(medioH);
      indice.write(indiceH);
      pulgar.write(pulgarH);
      break;
    case 1:
      menique.write(meniqueH);
      anular.write(anularH);
      medio.write(medioH);
      indice.write(indiceL);
      pulgar.write(pulgarH);
      break;
    case 2:
      menique.write(meniqueH);
      anular.write(anularH);
      medio.write(medioL);
      indice.write(indiceL);
      pulgar.write(pulgarH);
      break;
    // Continua per i vari livelli di attenzione...
  }
}
```

### Riassunto

1. **Lettura dei dati:** Il codice legge un byte alla volta dal buffer seriale.
2. **Identificazione del pacchetto:** Cerca i byte di sincronizzazione `0xAA` per iniziare a leggere un pacchetto di dati.
3. **Lettura del payload:** Dopo aver letto la lunghezza del payload, legge i dati e calcola il checksum per la verifica.
4. **Interpretazione dei dati:** Usa uno `switch` per interpretare i vari tipi di dati (qualità del segnale, attenzione, meditazione).
5. **Controllo dei servomotori:** Usa il valore di attenzione per determinare la posizione dei servomotori del braccio robotico.

Questo schema ti aiuta a capire come il codice riceve e interpreta i dati via Bluetooth e come utilizza questi dati per controllare il braccio robotico.


link utili:
https://www.researchgate.net/publication/377200718_An_Overview_of_Mindwave_Applications_Study_Cases
https://www.pantechsolutions.net/top-25-brain-computer-interface-projects
https://phdtopic.com/brain-computer-interface-project-ideas/
https://medium.com/@riazsulaimi/an-eeg-controlled-wheelchair-project-using-tgam-mindwave-eeg-sensor-android-arduino-ce710cce4dd6

https://www.ijitee.org/wp-content/uploads/papers/v8i11/K24530981119.pdf
