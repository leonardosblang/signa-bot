import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import init, Fore, Style
from infrastructure.config import config
# Use intelligent comprehensive adapters
from infrastructure.adapters.comprehensive_crawler import ComprehensiveCrawlerAdapter as SignaCrawlerAdapter
from infrastructure.adapters.knowledge_base_adapter import InMemoryKnowledgeBase
from infrastructure.adapters.intelligent_chatbot_adapter import IntelligentChatbotAdapter as OpenAIChatbotAdapter
from application.crawler_service import CrawlerService
from application.chatbot_service import ChatbotService

init(autoreset=True)

class SignaChatbotCLI:
    def __init__(self):
        self.knowledge_base = InMemoryKnowledgeBase()
        self.crawler = SignaCrawlerAdapter()
        self.chatbot = OpenAIChatbotAdapter(self.knowledge_base)
        self.crawler_service = CrawlerService(self.crawler, self.knowledge_base)
        self.chatbot_service = ChatbotService(self.chatbot, self.knowledge_base)
        
    async def initialize(self):
        print(f"{Fore.CYAN}=== Signa Chatbot ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Inicializando...{Style.RESET_ALL}")
        
        config.validate()
        
        data = await self.knowledge_base.get_all_data()
        if data['total_products'] == 0:
            print(f"{Fore.YELLOW}Base de conhecimento vazia. Iniciando crawling...{Style.RESET_ALL}")
            await self.crawl_site()
        else:
            print(f"{Fore.GREEN}Base de conhecimento carregada: {data['total_products']} produtos, {data['total_categories']} categorias{Style.RESET_ALL}")
    
    async def crawl_site(self):
        print(f"{Fore.YELLOW}Crawling do site Signa em progresso...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Isto pode demorar alguns minutos...{Style.RESET_ALL}")
        
        try:
            stats = await self.crawler_service.crawl_and_index()
            print(f"{Fore.GREEN}Crawling concluído!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Categorias: {stats['categories_crawled']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Produtos: {stats['products_crawled']}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Erro durante o crawling: {e}{Style.RESET_ALL}")
            if config.debug_mode:
                import traceback
                traceback.print_exc()
    
    async def run(self):
        await self.initialize()
        
        print(f"\n{Fore.CYAN}Chatbot pronto! Digite 'ajuda' para ver os comandos disponíveis.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Digite 'sair' para terminar.{Style.RESET_ALL}\n")
        
        while True:
            try:
                user_input = input(f"{Fore.GREEN}Você: {Style.RESET_ALL}")
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print(f"{Fore.YELLOW}Até logo!{Style.RESET_ALL}")
                    break
                    
                elif user_input.lower() == 'ajuda':
                    self.show_help()
                    
                elif user_input.lower() == 'stats':
                    await self.show_stats()
                    
                elif user_input.lower() == 'crawl':
                    await self.crawl_site()
                    
                elif user_input.lower() == 'limpar':
                    self.chatbot_service.clear_history()
                    print(f"{Fore.YELLOW}Histórico de conversa limpo.{Style.RESET_ALL}")
                    
                else:
                    response = await self.chatbot_service.chat(user_input)
                    print(f"\n{Fore.BLUE}Assistente: {Style.RESET_ALL}{response}\n")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Interrompido pelo usuário. Até logo!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Erro: {e}{Style.RESET_ALL}")
                if config.debug_mode:
                    import traceback
                    traceback.print_exc()
    
    def show_help(self):
        help_text = f"""
{Fore.CYAN}=== Comandos Disponíveis ==={Style.RESET_ALL}

{Fore.YELLOW}Perguntas sobre produtos:{Style.RESET_ALL}
- "tem caneca azul?" - Procura canecas azuis
- "mochilas baratas" - Procura mochilas com preço baixo
- "bolsas verdes" - Procura bolsas verdes
- "produtos de tecnologia" - Mostra produtos de tecnologia

{Fore.YELLOW}Comandos especiais:{Style.RESET_ALL}
- ajuda - Mostra esta mensagem
- stats - Mostra estatísticas da base de dados
- crawl - Atualiza a base de dados (crawl completo)
- limpar - Limpa o histórico de conversa
- sair - Termina o programa

{Fore.YELLOW}Exemplos de perguntas:{Style.RESET_ALL}
- "Quais são as categorias disponíveis?"
- "Tem mochilas vermelhas?"
- "Produtos até 5 euros"
- "O que é a Signa?"
"""
        print(help_text)
    
    async def show_stats(self):
        stats = await self.chatbot_service.get_stats()
        print(f"\n{Fore.CYAN}=== Estatísticas ==={Style.RESET_ALL}")
        print(f"Total de produtos: {stats['total_products']}")
        print(f"Total de categorias: {stats['total_categories']}")
        print(f"Mensagens na conversa: {stats['conversation_length']}\n")

async def main():
    cli = SignaChatbotCLI()
    await cli.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"{Fore.RED}Erro fatal: {e}{Style.RESET_ALL}")
        sys.exit(1)