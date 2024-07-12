# VAI TRABALHAR EM L ou MOMENTO FLETOR

condição=input("Qual condição de trabalho, em L ou Momento Fletor? ") 

# Dobramento por momento fletor

if condição=="Em L":
  
  def Força_de_DobramentoFLETOR():
    Espessura=float(input("Espessura: "))
    largura=float(input("largura: "))
    distância_dos_apoios=float(input("distância dos apoios: "))
    tensao_de_flexao=float(input("Sua tensão de flexão: "))

    Forçadedobramento=float((2*tensao_de_flexao*largura*Espessura**2)/(3*distância_dos_apoios))
    print("Força de dobramento= ",Forçadedobramento)

  Força_de_DobramentoFLETOR()

# Dobramento em L

if condição!="Em L":

  def Força_de_DobramentoL():
   EspessuraF = float(input("Espessura: "))
   larguraF = float(input("largura: "))
   tensao_de_dobra = float(input("Sua tensão de flexão: "))

   ForçadedobramentoL = float(((1/6)*tensao_de_dobra*larguraF*EspessuraF))
   print("Força de dobramento= ",ForçadedobramentoL)

  Força_de_DobramentoL()