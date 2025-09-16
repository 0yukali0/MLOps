from flytekit import ImageSpec, Resources, task
from flytekit.extras.accelerators import A10G
from flytekitplugins.inference import Model, Ollama
from openai import OpenAI

image = ImageSpec(
    name="ollama_serve",
    registry="localhost:30000",
    packages=["flytekitplugins-inference"],
    builder="default",
)

ollama_instance = Ollama(model=Model(name="google/gemma-3-4b-it"))


@task(
    container_image=image,
    pod_template=ollama_instance.pod_template,
)
def model_serving(user_prompt: str) -> str:
    client = OpenAI(base_url=f"{ollama_instance.base_url}/v1", api_key="ollama")  # api key required but ignored

    completion = client.chat.completions.create(
        model="google/gemma-3-4b-it",
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        temperature=0.5,
        top_p=1,
        max_tokens=1024,
    )

    return completion.choices[0].message.content