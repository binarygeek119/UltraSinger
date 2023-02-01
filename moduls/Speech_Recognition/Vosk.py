import wave
import json
import csv

from vosk import Model, KaldiRecognizer
from moduls.Speech_Recognition.VoskTranscribedData import VoskTranscribedData
from moduls.Audio.vocal_chunks import export_chunks_from_vosk_data, remove_silence_from_vosk_data


# todo: Rename to Transcoder?

def export_vosk_data_to_csv(vosk_transcribed_data, filename):
    """Export vosk data to csv"""
    print("Exporting Vosk data to CSV")

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ["word", "start", "end", "confidence"]
        writer.writerow(header)
        for i in range(len(vosk_transcribed_data)):
            writer.writerow(
                [vosk_transcribed_data[i].word, vosk_transcribed_data[i].start, vosk_transcribed_data[i].end,
                 vosk_transcribed_data[i].conf])


def transcribe_with_vosk(audio_filename, folder_name, model_path):
    # Code from here: https://towardsdatascience.com/speech-recognition-with-timestamps-934ede4234b2
    print("Transcribing {} with vosk and model {}".format(audio_filename, model_path))

    csv_filename = folder_name + "/_chunks.csv"

    model = Model(model_path)
    wf = wave.open(audio_filename, "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())

    recognizer.SetWords(True)

    # get the list of JSON dictionaries
    results = []
    # recognize speech using vosk model
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            part_result = json.loads(recognizer.Result())
            results.append(part_result)
    wf.close()  # close audiofile
    part_result = json.loads(recognizer.FinalResult())
    results.append(part_result)

    # convert list of JSON dictionaries to list of 'Word' objects
    vosk_transcribed_data = []
    for sentence in results:
        if len(sentence) == 1:
            # sometimes there are bugs in recognition
            # and it returns an empty dictionary
            # {'text': ''}
            continue
        for obj in sentence['result']:
            vtd = VoskTranscribedData(obj)  # create custom Word object
            vosk_transcribed_data.append(vtd)  # and add it to list

    # Todo: remove silent part from each word

    # output to the screen
    # todo: progress?
    # for word in vosk_transcribed_data:
    #    print(word.to_string())

    # todo: to own method
    vosk_transcribed_data = remove_silence_from_vosk_data(audio_filename, vosk_transcribed_data)
    export_chunks_from_vosk_data(audio_filename, vosk_transcribed_data, folder_name)
    export_vosk_data_to_csv(vosk_transcribed_data, csv_filename)

    return vosk_transcribed_data


class SpeechToText:
    pass