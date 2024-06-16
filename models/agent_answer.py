from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from operator import itemgetter


from db_xata.retriever import retriever_xata
from common.settings import settings
from models import agent_settings


class Agent:

    def chunk_of_docs(self, documents):
        """Функция формирует строку из номеров отобранных чанков."""
        content = ''
        for i, doc in enumerate(documents):
            content += f"№{i+1}(Chunk #{doc['chunk']}), "
        return content

    def documents_in_content(self, documents):
        """Функция преобразования списка документов в текст для LLM."""
        content = ''
        for i, doc in enumerate(documents):
            content += f"Document #{i+1} (Chunk #{doc['chunk']})\n{doc['content'].strip()}\n\n"
        return content.strip()

    def get_answer(
            self,
            question,
            filter_agent=agent_settings['agent_all'],
            router_name='',
            data_personal='',
            subquery_id=''):

        # Создание промта из шаблона.
        prompt_general = ChatPromptTemplate.from_template(
            filter_agent['template_prompt'])

        # Определение параметров модели LLM.
        llm = ChatOpenAI(
            model=settings.aa_model,
            temperature=settings.aa_temperature)

        # Запуск ретривера
        docs_xata = retriever_xata(
            query=question,
            type_search=settings.aa_type_search,
            top_k=settings.aa_top_k,
            filter_agent=filter_agent,
            subquery_id=subquery_id)

        # Подготовка контекста для LLM из возврвщенных документов.
        context = self.documents_in_content(docs_xata)

        # Определение цепочки.
        final_general_query = (
            {'context': context,
             'question': itemgetter('question'),
             'data_personal': itemgetter('data_personal')}
            | prompt_general
            | llm
            | StrOutputParser()
        ).with_config({"run_name": 'query', 'tags': [f'{router_name}']})

        # Выполнение запроса.
        answer = final_general_query.invoke({
            'question': question,
            'data_personal': data_personal,
        }, config={"callbacks": [settings.tracer]})

        return answer
