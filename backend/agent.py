import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from tavily import TavilyClient
from backend.prompts import (
    SIMPLE_PROMPT,
    REASONING_PROMPT,
    SOCIAL_PROMPT,
    ACADEMIC_PROMPT,
    FINANCE_PROMPT,
    SUMMARIZER_PROMPT,
    ROUTING_PROMPT
)
from backend.utils import aggregate_and_summarize
from langchain_tavily import TavilySearch, TavilyExtract, TavilyCrawl
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated

class State(TypedDict):
    messages: Annotated[list, add_messages]

class WebAgent:
    """
    Агент для веб-поиска с несколькими режимами:
    - Быстрый поиск (simple)
    - Глубокий анализ (deep/reasoning)
    - Социальный анализ (social)
    - Академический поиск (academic)
    - Финансовый анализ (finance)
    """
    
    def __init__(self, model_type: str = "openai"):
        self.model_type = model_type
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Инициализация модели в зависимости от типа
        if model_type == "anthropic":
            self.model = ChatAnthropic(
                model="claude-3-5-sonnet-20240620",
                temperature=0,
                max_tokens=4096,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            # Для OpenAI используем модель из переменных окружения или по умолчанию
            model_name = os.getenv("NANO_MODEL", "gpt-3.5-turbo")
            self.model = ChatOpenAI(
                model=model_name,
                temperature=0,
                max_tokens=4096,
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL") if os.getenv("OPENAI_BASE_URL") else None
            )

    def _get_model_with_tools(self, tools):
        """Получить модель с привязанными инструментами"""
        return self.model.bind_tools(tools)

    def build_graph(self) -> StateGraph:
        """
        Создать граф для стандартного режима (быстрый поиск или глубокий анализ)
        """
        from langgraph.prebuilt import ToolNode
        
        # Определение инструментов для стандартного режима
        tools = [
            TavilySearch(),
            TavilyExtract(),
            TavilyCrawl()
        ]
        
        tool_node = ToolNode(tools)
        model_with_tools = self._get_model_with_tools(tools)
        
        # Определение состояния графа
        workflow = StateGraph(State)
        
        # Добавление узлов
        def call_model(state: State) -> dict:
            messages = state["messages"]
            response = model_with_tools.invoke(messages)
            return {"messages": [response]}
            
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        # Добавление ребер
        workflow.add_edge("tools", "agent")
        
        # Условное ребро для определения, нужно ли использовать инструменты
        def should_continue(state: dict) -> str:
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
                return "tools"
            return END
            
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Установка начального узла
        workflow.set_entry_point("agent")
        
        return workflow
    
    def build_social_graph(self) -> StateGraph:
        """
        Создать граф для социального анализа
        """
        from langgraph.prebuilt import ToolNode
        
        # Инструменты для социального анализа (с фокусом на социальные платформы)
        tools = [
            TavilySearch(
                include_domains=["reddit.com", "twitter.com", "x.com", "vk.com", "habr.com"],
                time_range="week"
            ),
            TavilyExtract(),
            TavilyCrawl()
        ]
        
        tool_node = ToolNode(tools)
        model_with_tools = self._get_model_with_tools(tools)
        
        # Определение состояния графа
        workflow = StateGraph(State)
        
        # Добавление узлов
        def call_model(state: State) -> dict:
            messages = state["messages"]
            response = model_with_tools.invoke(messages)
            return {"messages": [response]}
            
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        # Добавление ребер
        workflow.add_edge("tools", "agent")
        
        # Условное ребро для определения, нужно ли использовать инструменты
        def should_continue(state: dict) -> str:
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
                return "tools"
            return END
            
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Установка начального узла
        workflow.set_entry_point("agent")
        
        return workflow
    
    def build_academic_graph(self) -> StateGraph:
        """
        Создать граф для академического поиска
        """
        from langgraph.prebuilt import ToolNode
        
        # Инструменты для академического поиска (с фокусом на академические источники)
        tools = [
            TavilySearch(
                include_domains=["arxiv.org", "semanticscholar.org"],
                time_range="year"
            ),
            TavilyExtract(),
            TavilyCrawl()
        ]
        
        tool_node = ToolNode(tools)
        model_with_tools = self._get_model_with_tools(tools)
        
        # Определение состояния графа
        workflow = StateGraph(State)
        
        # Добавление узлов
        def call_model(state: State) -> dict:
            messages = state["messages"]
            response = model_with_tools.invoke(messages)
            return {"messages": [response]}
            
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        # Добавление ребер
        workflow.add_edge("tools", "agent")
        
        # Условное ребро для определения, нужно ли использовать инструменты
        def should_continue(state: dict) -> str:
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
                return "tools"
            return END
            
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Установка начального узла
        workflow.set_entry_point("agent")
        
        return workflow
    
    def build_finance_graph(self) -> StateGraph:
        """
        Создать граф для финансового анализа
        """
        from langgraph.prebuilt import ToolNode
        
        # Инструменты для финансового анализа (с фокусом на финансовые источники)
        tools = [
            TavilySearch(
                topic="finance",
                include_domains=["finance.yahoo.com", "bloomberg.com", "reuters.com"],
                time_range="day"
            ),
            TavilyExtract(),
            TavilyCrawl()
        ]
        
        tool_node = ToolNode(tools)
        model_with_tools = self._get_model_with_tools(tools)
        
        # Определение состояния графа
        workflow = StateGraph(State)
        
        # Добавление узлов
        def call_model(state: State) -> dict:
            messages = state["messages"]
            response = model_with_tools.invoke(messages)
            return {"messages": [response]}
            
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        # Добавление ребер
        workflow.add_edge("tools", "agent")
        
        # Условное ребро для определения, нужно ли использовать инструменты
        def should_continue(state: dict) -> str:
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
                return "tools"
            return END
            
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Установка начального узла
        workflow.set_entry_point("agent")
        
        return workflow

    def run(self, query: str, mode: str = "fast") -> Dict[str, Any]:
        """
        Запустить агент с заданным запросом и режимом
        
        Args:
            query: Поисковый запрос пользователя
            mode: Режим работы ("fast", "deep", "social", "academic", "finance")
            
        Returns:
            Словарь с результатами поиска
        """
        # Выбор подходящего графа в зависимости от режима
        if mode == "social":
            workflow = self.build_social_graph()
            system_prompt = SOCIAL_PROMPT
        elif mode == "academic":
            workflow = self.build_academic_graph()
            system_prompt = ACADEMIC_PROMPT
        elif mode == "finance":
            workflow = self.build_finance_graph()
            system_prompt = FINANCE_PROMPT
        elif mode == "deep":
            workflow = self.build_graph()
            system_prompt = REASONING_PROMPT
        else:  # fast/simple mode
            workflow = self.build_graph()
            system_prompt = SIMPLE_PROMPT
            
        # Компиляция графа
        app = workflow.compile()
        
        # Подготовка сообщений
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        # Запуск графа
        result = app.invoke({"messages": messages})
        
        # Извлечение последнего сообщения
        last_message = result["messages"][-1]
        
        # Агрегация и суммирование результатов
        response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return {
            "response": response_text,
            "sources": []  # Источники будут добавлены в app.py
        }

    def route_query(self, query: str) -> str:
        """
        Route query to appropriate search mode using rule-based classification.
        Modes: 'fast', 'deep', 'social', 'academic', 'finance'
        """
        try:
            # Convert to lowercase for case-insensitive matching
            query_lower = query.lower()
            
            # Define keyword sets for each category
            social_keywords = {
                # Russian social networks and platforms
                'вконтакте', 'vk', 'ok.ru', 'одноклассники', 'дзен', 'zen', ' rutube', 'youtube',
                'reddit', 'twitter', 'facebook', 'instagram', 'linkedin', 'telegram', 'whatsapp',
                'твиттер', 'фейсбук', 'инстаграм', 'линкедин', 'телеграм', 'вотсап', 'ватсап',
                'сообщество', 'пользователи', 'обсуждение', 'пост', 'тренды', 'мнение', 'отзывы',
                'подписчики', 'лайки', 'репосты', 'хабр', 'vc.ru', 'vc', 'tjournal', 'dtf',
                'паблик', 'группа', 'канал', 'чат', 'форум', 'социальная сеть',
                # English social networks and platforms
                'social media', 'social network', 'community', 'users', 'discussion', 'post',
                'trends', 'opinion', 'reviews', 'followers', 'likes', 'shares', 'group', 'channel',
                'chat', 'forum', 'platform'
            }
            
            academic_keywords = {
                'научн', 'исследован', 'публикац', 'статья', 'paper', 'research', 'study', 'academic',
                'arxiv', 'ieee', 'springer', 'elsevier', 'nature', 'science', 'jstor', 'acm', 'acl',
                'conference', 'journal', 'thesis', 'диссертаци', 'магистерск', 'курсов', 'лекци',
                'теори', 'алгоритм', 'метод', 'nlp', 'нейронн', 'машинн', 'обучен', 'ml', 'ai',
                'computer science', 'математик', 'статистик', 'эксперимент', 'анализ', 'обзор',
                # English academic terms
                'scientific', 'publication', 'article', 'paper', 'research', 'study', 'academic',
                'conference', 'journal', 'thesis', 'dissertation', 'master', 'course', 'lecture',
                'theory', 'algorithm', 'method', 'computer science', 'mathematics', 'statistics',
                'experiment', 'analysis', 'survey', 'review'
            }
            
            finance_keywords = {
                'цена', 'стоимость', 'стоит', 'акции', 'stock', 'share', 'investment', 'invest',
                'рынок', 'биржа', 'трейдинг', 'trading', 'currency', 'валюта', 'доллар', 'euro',
                'рубль', 'курс', 'exchange', 'forex', 'крипт', 'bitcoin', 'ethereum', 'btc', 'eth',
                'wallet', 'кошелек', 'прибыль', 'доход', 'убыток', 'loss', 'profit', 'dividend',
                'дивиденд', 'портфель', 'portfolio', 'etf', 'фонд', 'облигаци', 'credit', 'кредит',
                'loan', 'заем', 'ипотек', 'mortgage', 'insurance', 'страхован', 'pension', 'пенси',
                'налог', 'tax', 'budget', 'бюджет', 'экономик', 'inflation', 'инфляци', 'deflation',
                'recession', 'рецесси', 'yahoo finance', 'marketwatch', 'bloomberg', 'reuters',
                # English finance terms
                'price', 'cost', 'stocks', 'shares', 'investment', 'invest', 'market', 'exchange',
                'trading', 'currency', 'dollar', 'euro', 'ruble', 'rate', 'exchange rate', 'forex',
                'crypto', 'bitcoin', 'ethereum', 'wallet', 'profit', 'income', 'loss', 'dividend',
                'portfolio', 'etf', 'fund', 'bond', 'credit', 'loan', 'mortgage', 'insurance',
                'pension', 'tax', 'budget', 'economics', 'inflation', 'deflation', 'recession'
            }
            
            # Keywords indicating need for deep analysis
            deep_analysis_indicators = {
                'анализир', 'исслед', 'сравн', 'объясн', 'разбер', 'подробн', 'detail', 'analyze',
                'compare', 'explain', 'comprehensive', 'thorough', 'in-depth', 'evaluate', 'assess',
                'review', 'examine', 'study', 'investigate', 'scrutinize', 'dissect', 'elaborate',
                'рассмотр', 'проанализир', 'изуч', 'оцени', 'провер', 'проверь', 'проверить',
                # English deep analysis terms
                'analyze', 'investigate', 'examine', 'study', 'review', 'evaluate', 'assess',
                'compare', 'explain', 'comprehensive', 'thorough', 'in-depth', 'detailed',
                'scrutinize', 'dissect', 'elaborate', 'explore', 'inspect', 'probe', 'delve'
            }
            
            # Simple/fast query indicators (short, factual questions)
            fast_query_indicators = {
                'что такое', 'кто тако', 'какой', 'какая', 'какое', 'каков', 'какова', 'каково',
                'где', 'когда', 'почему', 'зачем', 'сколько', 'как много', 'как мало', 'как часто',
                'is', 'are', 'what', 'where', 'when', 'why', 'how', 'who', 'which', 'how much',
                'how many', 'how often', 'what is', 'what are', 'where is', 'where are', 'каковы',
                # English fast query indicators
                'what is', 'what are', 'who is', 'who are', 'where is', 'where are', 'when is',
                'when are', 'why is', 'why are', 'how is', 'how are', 'what does', 'how does',
                'what do', 'how do', 'define', 'definition', 'meaning', 'explain briefly'
            }
            
            # Check for social network queries first (highest priority)
            if any(keyword in query_lower for keyword in social_keywords):
                return 'social'
            
            # Check for academic queries
            if any(keyword in query_lower for keyword in academic_keywords):
                return 'academic'
            
            # Check for finance queries
            if any(keyword in query_lower for keyword in finance_keywords):
                return 'finance'
            
            # Check for deep analysis queries
            if any(keyword in query_lower for keyword in deep_analysis_indicators):
                return 'deep'
            
            # Check for simple/fast queries
            if any(keyword in query_lower for keyword in fast_query_indicators):
                # Additional check: short queries are more likely to be fast
                if len(query.split()) <= 6:
                    return 'fast'
            
            # Default to fast for very short queries
            if len(query.split()) <= 4:
                return 'fast'
                
            # Default to deep for longer, unclassified queries
            return 'deep'
            
        except Exception as e:
            print(f"Routing error: {e}")
            return 'fast'  # Safe fallback
