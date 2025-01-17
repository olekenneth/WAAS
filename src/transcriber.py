import whisper

def transcribe(filename, requestedModel, task, language):
    model = whisper.load_model(requestedModel)

    return model.transcribe(filename, language=language, task=task)
