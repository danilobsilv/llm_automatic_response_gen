import time  # <--- 1. Importe a biblioteca de tempo
from src.llm.openai_gpt4 import OpenAiGPT4
from src.llm.google_gemini import GoogleGemini
from src.llm.meta_llama3 import MetaLlama3
from src.prompt_engineering.prompts_manager import PromptManager


def execute_agents():
    prompt_manager = PromptManager()

    # --- models ---
    models_temperature = 0.7
    modelos = {
        # "OpenAI": OpenAiGPT4(model_name="gpt-4o", temperature=models_temperature),
        "Gemini": GoogleGemini(model_name="gemini-2.5-pro", temperature=models_temperature),
        # "Llama3": MetaLlama3(model_name="llama3", temperature=models_temperature)
    }

    user_comments_before_llm = [
        """A comida continua boa porém o atendimento em relação quando inaugurou não conseguiu manter o padrão. Os Garçons precisam ser mais profissionais e mais atenciosos.""",
        """O local atende o que se propõe. Pratos bem servidos e saborosos mas costumam demorar muito e os garçons não são atenciosos.""",
        """O local em si é agradável, mas a música que eles tocam ao vivo lhe dá um ar de boteco. A comida é ruim. Em geral uns poucos camaroes mergulhados em queijo e batata palha. Se formos comparar a Camaroes e Nau em Natal, de fato se moatra um lugar pra não voltar. Atendimento também pouco cortês e lento. Não recomendo""",
        """ Lagosta Com Arroz dos Mares. - Quatro caudas de lagostas grelhadas, salpicadas com alho frito. Servidas sobre uma mistura de arroz com nata, leite de coco, mix de pimentões, cebola, cebolinha e coentro. É frustrante passar 1h na fila pra uma mesa, esperar mais quase 45min para chegar o prato principal e nos trazerem “1 kg” de arroz que ao contrário da descrição não tem gosto nata e o leite de coco é um mero “oi, passei por aqui”. O tamanho dessas caudas de lagosta são menores que muitos camarões. Eram lagostas anãs? Ao virem a foto, descartem a casca, o que sobra é algo equivalente do tamanho de um camarão para tempurá. O descontentamento nos abateu e comunicamos a gerência e ao garçom. No final pediram para eu preencher um questionário perguntando a nossa opinião e nos informaram que nós não éramos os únicos a reclamar do tamanho da lagosta, e que aquele papel era importante ser preenchido para a reclamação chegar na direção do Coco Bambu. Fizemos a nossa parte lá, e agora fazemos nossa parte por aqui. Nos sentimos frustrados e lesados. E não precisa dessa formalidade toda para verem que o tamanho da lagosta não está adequada. Não pedimos um prato de R$185,00 para nos satisfazermos com o acompanhamento (arroz), nós queríamos o principal (lagosta). E se a lagosta não está no tamanho ideal, que seja informado ao cliente no momento do pedido, assim teremos a chance de escolhermos arriscar ou mudarmos o pedido, ou então que façam algo para compensar tal deficiência momentânea, afinal pagamos o valor integral do prato. Coco Bambu deve zelar pelo consumidor Amazonense, que lota aquele restaurante no almoço e jantar todos os dias, servindo produtos com o padrão de qualidade à altura do restaurante.""",
        """Fui no almoço. Primeiro o garçom foi inconveniente ao insistir no que deveríamos pedir, pedimos de entrada um camarão de 76 reais que não estava bem preparado. Depois de muita dúvida pois o cardápio é muito extenso e repetitivo, pedimos um camarão Iracema(157 reais) que no cardápio dizia servir até 4 pessoas, talvez serviria se a quarta pessoa aceitasse comer só arroz de leite, pois sobrou uma quantidade enorme, camarão mesmo que é bom achei que só come no máximo 3. De acompanhamento uma porção de macaxeira que nem comemos pois estava dura. Resultado, 300 reais a conta pra três pessoas, lugar bonito mas a comida, o atendimento e o preço não valeu a pena.""",
        """Excelente experiência neste maravilhoso restaurante. Ambiente muito bem requintado e na comida maravilhosa. O garçom Wellington nos prestou um excelente atendimento, sendo muito atencioso, simpático e nos deu ótimas dicas. Parabéns! Voltarei mais vezes.""",
        """Sou cliente do Coco bambu e venho observado que o padrão no atendimento só vem caindo cada vez mais, ao contrario de outros restaurante o coco começou com um atendimento excelente, e conforme o tempo foi passando piora cada vez mais. No final de semana tive a minha pior experiencia fomos atendido por um garçom totalmente despreparado, e após diversos erros resolvemos pedir para chamar o Gerente e veio o Metre chamado Augusto, esse nem se quer ouviu as nossas observações e foi muito arrogante.""",
        """Comida com aparência requentada.Comida que você percebe que não foi feita na hora.Se você pedir um prato que tenha arroz, 90% do prato será de arroz, e arroz duro, aparentemente velho.Aliás, só frequento esse restautante, a contragosto, quando tem algum evento (aniversário, p. Exemplo).Não acho esse restautante nada demais.""",
        """Já fui ao Coco Bambu Brasília e RJ e nunca tive uma experiência tão ruim como na unidade Manaus. O prato demorou literalmente 1:10h para chegar e quando chegou veio mal servido e frio. Foi um prato de peixe, acho que só devem saber fazer camarão no restaurante... Depois disso tudo acho que o mínimo era não terem me cobrado o prato, mas fizeram questão de cobrar. Péssima experiência, se não puder comer camarão não va nesse restaurante!""",
        """Já não é a primeira vez que vou ao happy hour do coco bambu e me dizem que os itens promocionais estão em falta. Agora na minha recente visita, pedi uma cesta de pastéis e me informaram que não tinha massa, porém assim que acabou o happy hour, umas 20:20 já estavam entregando pedidos de pastéis nas outras mesas. Ou seja, só não tinha pastel na hora da promoção, fora do happy hour tem. Muita falta de respeito com o consumidor, visto que, se estão disponibilizando horário promocional, devem ser justos e honrar, não simplesmente dizer que não tem e logo em seguida começar a servir . Péssima forma de prestar serviço. Ainda que seja de promoção esta sendo pago!""",
        """Experiência horrível. Lugar desorganizado. Garçons anotam o pedido e esquecem. Pedi um sanduíche demorou 50 minutos. 1 chopp demorou 70 minutos. Não recomendo. A comida não sei se é boa pois fui embora""",
        """Os pratos demoraram uma hora, sendo o último entregue uma refeição kids, notadamente menor. Comida fria, porção medíocre. Péssima escolha em Manaus!""",
        """Demora demais pra vir a comida pra mesa. Uma eternidade. Se não tem estrutura, fecha as portas. É uma vergonha. Aconteceu em outras mesas também. Muita gente saiu reclamando.""",
        """Cheguei no local para tirar dúvida sobre um prato o restaurante tinha pouquíssima pessoas, perguntei o Garçon sobre um prato pra tirar dúvida ele não soube dizer chamou outro Garçon, até aí tudo bem… pedi pra chamar o gerente mais de 30 minutos para o gerente vir, isso o restaurante pouquíssima mesa com pessoas O horário que eu cheguei no local era 15:50 Atendimento péssimo O chopp quente. Não indico A comida estava boa, valeu a pena esperar Não indico coco bambu para ninguém, não é a primeira vez que acontece comigo. Esse de MANAUS impossível indicar""",
        """Fomos comemorar o aniversário de 30 anos de meu marido e nossos 11 anos juntos. Nos programamos para or no horário de happy hour. No site oficial diz que os valores do happy hour valem de 17 as 20. No cocô bambu de Manaus eles mudam o horário ao bem entender. Chegamos as 19 e o valor hour havia finalizado...Não gostei, me senti enganada, entrei no site oficial e aparentemente a informação oficial não vale nada. Depois disso ficamos um pouco decepcionados com o restaurante.""",
        """Serviços horríveis Comida de má qualidade Bebidas em baixa refrigeração Todos os atendentes de mau humor Guardanapos próprios para lanchonetes Melhor teria sido ir comer no Marios’s Lanche""",
        """Frete de R$15,00, 45min para receber um prato caro e frio. NAO RECOMENDO! Liguei para o restaurante para reclamar, não tão nem aí...""",
        """Preços não condizem com a experiencia nada agradavel no local, vale a visita, mas não vale o retorno."""
    ]

    user_comments_after_llm = [
        """Experiência muito agradável, ao chegar pedimos mesa para 2, e mesmo o ambiente estando bem cheio conseguiram um local agradável na parte superior do restaurante, logo uma música eletrônica nos chamou atenção e curiosidade, o sr. Yuri nos atendeu muito bem e fez a gentileza de nos apresentar de onde vinha o som, (em uma parte reservada há DJ, jogo de luzes, como uma balada, onde pode jantar, beber reservar para comemorações etc muito atrativo funciona dias de sexta e sábado).
        a comida estava muito boa, e pedimos drinks temáticos, que estavam saborosos. Voltaremos com certeza!""",
        """Boa noite! Fui muito bem atendida desde da proposta inicial, a moça me ajudou com a proposta para que coubesse dentro do meu orçamento da forma que imaginava então devido a experiência ficou como eu queria até para firma de pagamento. Os meninos Matheus, Lucas e Giovanna foram espetacular me ajudando a montar a mesa exatamente como queria até melhor com todo material que trouxe me passando segurança em todo evento.""",
        """Impecável. Fomos almoçar no Coco Bambu. Nem sei por onde começar. Se pelo serviço e simpatia do empregado Klisman se pela comida em si. Provei talvez o melhor tornedó / filé da minha vida e, atenção, já estou bem perto dos 70. Recomendo.""",
        """O famoso coco bambu,deixou a desejar ... oferece um cardápio online aonde os preços estão todos alterados no sistema..e deixa nos clientes insatisfeito na hora de efetuar o pedido porq não sabemos qual preço certo""",
        """Experiência muito agradável, ao chegar pedimos mesa para 2, e mesmo o ambiente estando bem cheio conseguiram um local agradável na parte superior do restaurante, logo uma música eletrônica nos chamou atenção e curiosidade, o sr. Yuri nos atendeu muito bem e fez a gentileza de nos apresentar de onde vinha o som, (em uma parte reservada há DJ, jogo de luzes, como uma balada, onde pode jantar, beber reservar para comemorações etc muito atrativo funciona dias de sexta e sábado).""",
        """Venho todo mês com esposo após o sábado da minha pós na iPog assim como vi hj amigos e professores . E a demora do shopping durante a promoção o Happy hour é absurda, principalmente após as 19h. Se atendessem em menor tempo possível, iriam proporcionar melhor experiência ao cliente. Maior venda dos produtos. E o pior pagar o couvert quase no final da experiência não tá certo. Deve ser pelo menos com uma hora de curtir o happy""",
        """Boa noite! Fui muito bem atendida desde da proposta inicial, a moça me ajudou com a proposta para que coubesse dentro do meu orçamento da forma que imaginava então devido a experiência ficou como eu queria até para firma de pagamento. Os meninos Matheus, Lucas e Giovanna foram espetacular me ajudando a montar a mesa exatamente como queria até melhor com todo material que trouxe me passando segurança em todo evento.""",
        """Lugar excelente para um happy hour, ou jantar com a familia. Lugar acolhedor, com sofisticação. Uma observação o feijão baião estava muito al dente, poderia ser um mais mácio, o serviço é ótimo. Pagamento de couver e gaçons é opcional. Bom lugar""",
        """Ambiente aconchegante. Comida deliciosa, ótimo atendimento, a cantora Nara da Mata impecável, o nosso atendente Rodrigo super gentil e atencioso. Grata pela experiência, voltarei outras vezes com certeza.""",
        """Quero deixar um agradecimento especial ao garçom Marques pelo atendimento incrível! Sua atenção, simpatia e profissionalismo fizeram toda a diferença na nossa experiência. Obrigado por tornar nossa refeição ainda mais especial! Você é demais!""",
        """Impecável. Fomos almoçar no Coco Bambu. Nem sei por onde começar. Se pelo serviço e simpatia do empregado Klisman se pela comida em si. Provei talvez o melhor tornedó / filé da minha vida e, atenção, já estou bem perto dos 70. Recomendo.""",
        """Tivemos uma ótima experiência na unidade Coco Bambu Ponta Negra, em Manaus Um excelente atendimento com o garçom Audir, super gentil e atencioso. O Arthur também nos ofereceu um ótimo atendimento. Estão de parabéns!""",
        """Comida indicada muito gostosa. Meu filho amou! Ainda levamos para casa dele um boa porção. Seu Ademar e seu Ezequiel nos atenderam super bem. Ao ponto de meu filho mais novo levantar e dar um abração no seu Alelar.""",
        """Comi uma pescada amarela ao molho de alcaparras ontem. E o peixe estava estragado. Meu marido amanheceu com desarranjo intestinal. Eu avisei a atendente sobre a textura do peixe estar estranha um peixei em posta parecia um purê quando se comia. Estou grávida e pegar uma infecção simplesmente é risco de perder o bebê.""",
        """Gostaria aqui de deixar minha avaliação pela comida maravilhosa e tb pelo atendimento do garçom Hermano e tb a Amanda mas em geral todos atendentes são educados e prestativos! Super recomendo esse local""",
        """Espaço muito aconchegante. Fomos muito bem recepcionados pelo Ronaldo e Israel, com certeza um espaço incrível para vir mais vezes.""",
        """Experiência sempre incrível nesse restaurante que já é um dos meus favoritos, sem contar o atendimento impecável do garçom Ronaldo e do Israel, sem dúvidas um dos melhores atendimento que já tivemos.""",
        """Ótima!!! Ótimo atendimento (pela Carol, uma querida), ambiente agradável, bonito, música ambiente na medida certa! Muito bom.""",
    ]

    # Lista para armazenar as respostas e os tempos
    generated_responses_list = []

    # Define a persona e o tipo de prompt
    persona = "sophisticate_and_formal"
    prompt_type = "zero_shot"

    # Pega a instância do modelo
    model_name = "Gemini"
    model_instance = modelos[model_name]

    print(f"\n{'=' * 20} Usando Modelo: {model_name} {'=' * 20}")
    print(f"Testando Persona: {persona.replace('_', ' ').title()}")

    # Prepara o prompt do sistema uma única vez
    try:
        system_prompt = prompt_manager.get_prompt(
            prompt_type=prompt_type,
            persona=persona
        )
    except (ValueError, Exception) as e:
        print(f"Erro ao carregar o prompt: {e}")
        return

    # Itera sobre cada comentário na lista
    for i, user_comment in enumerate(user_comments_before_llm):
        print(f"--> Processando comentário {i + 1}/{len(user_comments_before_llm)}")
        try:
            # --- 2. MEDIÇÃO DE TEMPO ---
            start_time = time.time()  # Marca o tempo inicial

            response = model_instance.generate(
                system_prompt=system_prompt,
                user_input=user_comment
            )

            end_time = time.time()  # Marca o tempo final
            processing_time = round(end_time - start_time, 2)  # Calcula a diferença

            # 3. Adiciona a resposta e o tempo na lista
            generated_responses_list.append({
                "response": response,
                "time": processing_time
            })
            print(f"    ...concluído em {processing_time} segundos.")


        except (ValueError, Exception) as e:
            print(f"    Erro ao gerar resposta para o comentário {i + 1}: {e}")
            generated_responses_list.append({
                "response": f"ERRO: {e}",
                "time": -1
            })

    # Imprime a lista final com todas as respostas e seus tempos
    print("\n\n" + "=" * 20 + " LISTA DE RESPOSTAS GERADAS " + "=" * 20)
    for i, item in enumerate(generated_responses_list):
        print(f"\nRESPOSTA {i + 1} (Tempo: {item['time']}s):\n{item['response']}\n" + "-" * 40)