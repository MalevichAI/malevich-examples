# Duolingo :rocket:

This example is a multi-modal flow with moderate complexity and shows the power of Malevich. Malevich has no association with Duolingo.

Whilst learning a new language, we wanted to practice speaking about our surroundings. This example flow takes a picture and returns an audio of a story based on that input. This is a public flow available on Malevich, click here to try it out!

## Flow

To execute the above functionality the flow will execute the following steps:

- Download a new picture from the Cloud Storage
- Detect objects on the image (Сomputer Vision)
- Write a story about the objects (LLM)
- Translate the story to another language
- Create speech from the translated story (TTS)
- Post the output audio file to the endpoint

## Idea

```mermaid
graph LR
A[Download image] --> B[Detect objects]
B --> C[Write a story]
C --> D[Translate story]
D --> E[Create speech]
E --> F[Post audio]
```

## See also

- [Duolingo Flow](https://space.malevich.ai/workspace?compId=io.whywhy.newsletter)
- [Malevich Documentation](https://docs.malevich.ai/docs/examples/duolingo)




