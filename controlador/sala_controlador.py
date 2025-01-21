from abstrato.controlador_entidade_abstrata import ControladorEntidadeAbstrata
from entidade.sala import Sala
from exception.sala_nao_encontrada import SalaNaoEncontrada
from visao.sala_visao import SalaVisao
from DAO.sala_dao import SalaDAO
from exception.cancelopexeception import CancelOpException

class SalaControlador(ControladorEntidadeAbstrata):
    def __init__(self, sistema_controlador):
        self.__sistema_controlador = sistema_controlador
        self.__salavisao = SalaVisao()
        self.__sala_DAO = SalaDAO()


    def adicionar_sala(self):
        try:
            dados_sala = self.__salavisao.pega_dados_sala()
            numero = dados_sala["numero"]
            capacidade = dados_sala["capacidade"]

            if capacidade <= 0:
                raise ValueError(f"Capacidade inválida.")

            try:
                self.busca_sala(numero)
                raise Exception(f"Sala {numero} já está cadastrada.")
            except SalaNaoEncontrada:
                nova_sala = Sala(dados_sala["numero"],dados_sala["capacidade"])
                # USO DE DAO PARA SERIALIZAÇÃO
                self.__sala_DAO.add(nova_sala)
                self.__salavisao.mostra_mensagem(f"Sala {numero} foi adicionada com sucesso!")
        except ValueError as ve:
            self.__salavisao.mostra_mensagem(f"Erro: {ve}")
        except CancelOpException:
            pass
        except Exception as e:
            self.__salavisao.mostra_mensagem(f"Erro: {e}")

    def atualizar_sala(self):
        try:
            self.lista_salas()
            numero = self.__salavisao.seleciona_sala()
            sala = self.busca_sala(numero)

            nova_capacidade = self.__salavisao.pega_novos_dados_sala()

            if nova_capacidade <= 0:
                raise ValueError(f"Capacidade inválida.")

            sala.capacidade = nova_capacidade

            self.__sala_DAO.update(sala)
            self.lista_salas()
        # self.__salavisao.mostra_mensagem(f"Sala {numero} atualizada com sucesso!")
        except SalaNaoEncontrada as e:
            self.__salavisao.mostra_mensagem(f"Erro: {e}")
        except CancelOpException:
            pass

    def busca_sala(self, numero):
        salas = self.__sala_DAO.get_all()
        for sala in salas:
            if sala.numero == numero:
                return sala
        raise SalaNaoEncontrada(numero)

    def remover_sala(self):
        """
        Permite ao usuário selecionar uma sala e a remove do DAO.
        """
        try:
            numero = self.lista_salas(selecionar=True)
            if numero is None:
                return  # Operação cancelada pelo usuário

            self.__sala_DAO.remove(numero)
            self.__salavisao.mostra_mensagem(f"Sala {numero} foi removida com sucesso.")
        except SalaNaoEncontrada as e:
            self.__salavisao.mostra_mensagem(f"Erro: {e}")
        except CancelOpException:
            pass

    def lista_salas(self, selecionar=False):
        """
        Lista todas as salas cadastradas.
        Se `selecionar` for True, retorna o número da sala selecionada.
        """
        salas = self.__sala_DAO.get_all()
        if not salas:
            self.__salavisao.mostra_mensagem("Nenhuma sala cadastrada.")
            return None

        salas_info = [{"numero": sala.numero, "capacidade": sala.capacidade} for sala in salas]
        try:
            return self.__salavisao.exibe_lista_salas(salas_info, selecionar)
        except CancelOpException:
            return None

    def retornar(self):
        self.__sistema_controlador.abre_tela()

    def abre_tela(self):
        lista_opcoes = {1: self.adicionar_sala, 2: self.atualizar_sala, 3: self.remover_sala, 4: self.lista_salas, 0: self.retornar}

        continua = True
        while continua:
            lista_opcoes[self.__salavisao.tela_opcoes()]()
