VISAO GERAL:
Este script aplica o algoritmo VND (Variable Neighborhood Descent) em conjunto com o Framework TF, para encontrar um bom conjunto de otimizacoes ao utilizar o compilador Clang em determinado programa.

PRE-REQUISITOS:
- Python (https://www.python.org/)
- Clang (https://clang.llvm.org/)
- TF Framework (https://github.com/guilhermeleobas/tf.git)

USO:
- Primeiramente, este script "VND_Opt_Compile.py" deve estar no diretorio raiz do Framewrok TF (mesmo diretorio em que se encontra o  "run.sh" do TF). Ou entao, configure o diretorio do TF pelo argumento -d ou --dir.
- O Framewrok TF deve estar configurado para compilar e executar apenas um programa.
- Executando: python VND_Opt_Compile.py [opcao] <valor>

OPCOES:
-l <valor> ou --level <valor>
Nivel maximo: Deve estar entre 1 e 5. Determina qual o nivel maximo de vizinhanca gerada. Quanto maior o nivel, maior sera a vizinhanca gerada, obtendo uma otimizacao mais precisa, com gasto maior de tempo para obte-la. Por padrao o algoritmo executa com nivel maximo = 3.

-d <diretorio> ou --dir <diretorio>
Diretorio do TF: Especifique o diretorio do Framework TF. Por padrao o algoritmo utiliza o diretorio atual.

-a <valor> ou --accuracy <valor>
Precisao no tempo de execucao: Determina a precisao ao calcular o tempo de execucao dos programas compilados. Se accuracy = 2 por exemplo, faz a media de 2 execucoes. Por padrao o algoritmo executa com accuracy = 3.

-h ou --help
Exibe mensagem informativa sobre o algoritmo.


~ Desenvolvido por William Rodrigues.
