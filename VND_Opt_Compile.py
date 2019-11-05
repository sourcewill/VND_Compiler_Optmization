#-------------------------------------------------------------------------------

# Aplicacao do Algoritmo VND (Variable Neighborhood Descent) para exploracao de
# um bom conjunto de otimizacoes na aplicacao do compilador clang.

# Desenvolvido por William Rodrigues @ UEM 2019.

#-------------------------------------------------------------------------------

import getopt
import sys
import os

# Variavei Globais

DIR_TF = '.' # Diretorio do Framework TF
TIME_ACCURACY = 3 # Precisao no calculo de tempo de execucao (Por padrao definido como 3)

CURRENT_LEVEL = None # Nivel atual
MAX_LEVEL = 3 # Nivel maximo (Por padrao definido como 3)
BEST_SOLUTION = None # Melhor solucao
BEST_SOLUTION_TIME = None # Tempo da melhor solucao

# Conjunto de otmimizacoes O3
opt_arguments = "-tti -tbaa -scoped-noalias -assumption-cache-tracker -targetlibinfo -verify -ee-instrument -simplifycfg -domtree -sroa -early-cse -lower-expect -targetlibinfo -tti -tbaa -scoped-noalias -assumption-cache-tracker -profile-summary-info -forceattrs -inferattrs -callsite-splitting -ipsccp -called-value-propagation -globalopt -domtree -mem2reg -deadargelim -domtree -basicaa -aa -loops -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -simplifycfg -basiccg -globals-aa -prune-eh -inline -functionattrs -argpromotion -domtree -sroa -basicaa -aa -memoryssa -early-cse-memssa -speculative-execution -domtree -basicaa -aa -lazy-value-info -jump-threading -lazy-value-info -correlated-propagation -simplifycfg -domtree -basicaa -aa -loops -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -libcalls-shrinkwrap -loops -branch-prob -block-freq -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -pgo-memop-opt -domtree -basicaa -aa -loops -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -tailcallelim -simplifycfg -reassociate -domtree -loops -loop-simplify -lcssa-verification -lcssa -basicaa -aa -scalar-evolution -loop-rotate -licm -loop-unswitch -simplifycfg -domtree -basicaa -aa -loops -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -loop-simplify -lcssa-verification -lcssa -scalar-evolution -indvars -loop-idiom -loop-deletion -loop-unroll -mldst-motion -aa -memdep -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -gvn -basicaa -aa -memdep -memcpyopt -sccp -domtree -demanded-bits -bdce -basicaa -aa -loops -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -lazy-value-info -jump-threading -lazy-value-info -correlated-propagation -domtree -basicaa -aa -memdep -dse -loops -loop-simplify -lcssa-verification -lcssa -aa -scalar-evolution -licm -postdomtree -adce -simplifycfg -domtree -basicaa -aa -loops -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -barrier -elim-avail-extern -basiccg -rpo-functionattrs -globalopt -globaldce -basiccg -globals-aa -float2int -domtree -loops -loop-simplify -lcssa-verification -lcssa -basicaa -aa -scalar-evolution -loop-rotate -loop-accesses -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -loop-distribute -branch-prob -block-freq -scalar-evolution -basicaa -aa -loop-accesses -demanded-bits -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -loop-vectorize -loop-simplify -scalar-evolution -aa -loop-accesses -loop-load-elim -basicaa -aa -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -simplifycfg -domtree -loops -scalar-evolution -basicaa -aa -demanded-bits -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -slp-vectorizer -opt-remark-emitter -instcombine -loop-simplify -lcssa-verification -lcssa -scalar-evolution -loop-unroll -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instcombine -loop-simplify -lcssa-verification -lcssa -scalar-evolution -licm -alignment-from-assumptions -strip-dead-prototypes -globaldce -constmerge -domtree -loops -branch-prob -block-freq -loop-simplify -lcssa-verification -lcssa -basicaa -aa -scalar-evolution -branch-prob -block-freq -loop-sink -lazy-branch-prob -lazy-block-freq -opt-remark-emitter -instsimplify -div-rem-pairs -simplifycfg -verify -domtree"

opt_names = [] # Vetor a ser preenchido com os nomes das otimizacoes
opt_boolean = [] # Vetor para manipulacao da solucao, referencia o vetor de nomes


# Gera a estrutura de dados para manipulcao do problema:
# Vetores de nomes e booleans a partir das otimizacoes.
def generate_opt_arrays():

    global opt_arguments
    global opt_names
    global opt_boolean

    opt_names = opt_arguments.split()
    lengh = len(opt_names)

    # Inicializa todas as otmizacoes como True (O3)
    for _ in range(lengh):
        opt_boolean.append(True)


# Gera uma estrutura de vizinhanca baseada no nivel.
# Quanto maios o nivel, maior a vizinhanca gerada.
# current: deve conter a solucao atual
# level: corresponde ao nivel (entre 1 e 5)
def generate_neighbor(current, level):

    if level == 1:
        return generate_neighbor_partitions(current, 50)

    if level == 2:
        return generate_neighbor_partitions(current, 20)

    if level == 3:
        return generate_neighbor_partitions(current, 10)

    if level == 4:
        return generate_neighbor_partitions(current, 5)

    if level == 5:
        return generate_neighbor_partitions(current, 2)


# Funcao auxiliar na geracao de vizinhanca.
# Gera a vizinhanca repartindo-a em particoes, e causando
# alteracoes em cada particao para cada vizinho gerado.
def generate_neighbor_partitions(current, partitions):

    neighbor = []
    tamanho = len(current)
    
    for i in range(0, tamanho, partitions):
        aux = current[:]
        for j in range(partitions):
            if((i+j) < tamanho):
                aux[i+j] = not(aux[i+j])
        neighbor.append(aux)

    return neighbor


# Retorna uma string com os nomes (em vet_names) baseado nas respectivas
# flags setadas no vetor (vet_boolean) de uma determinada otimizacao
def opt_boolean_to_names(vet_boolean, vet_names):

    names = ''

    for i, flag in enumerate(vet_boolean):
        if flag:
            names = names + ' ' + vet_names[i]

    return names


# Obtem o tempo de execucao de um programa a partir do arquivo run.log
# gerado pelo framework TF ao executar.
def get_time_run_log():

    arq = open(DIR_TF + '/run.log', 'r')

    text = arq.readlines()[1]
    time = text.split()[3]

    arq.close()

    return float(time)


# Compila uma determinada solucao e calcula o tempo
# de execucao do codigo gerado pela mesma
# solution: vetor de Booleans que representa as otimizacoes
def calculate_time(solution, accuracy):

    global opt_names

    # Compilando com um conjunto de otimizacoes
    command_line = 'cd ' + DIR_TF + ' && COMPILE=1 EXEC=0 OPT="' + opt_boolean_to_names(solution, opt_names) + '" ./run.sh'
    #print('\nCOMANDO: ' + command_line)
    os.system(command_line)

    # Calculando media de tempo de execucao do programa
    time = 0
    for _ in range(accuracy):
        os.system('cd ' + DIR_TF + ' && COMPILE=0 EXEC=1 ./run.sh')
        time += get_time_run_log()

    return ( time / accuracy )


# Busca local utilizando a estrategia do primeiro
# elemento que melhora a solucao atual
def local_search_first(current):

    global CURRENT_LEVEL
    global BEST_SOLUTION
    global BEST_SOLUTION_TIME
    global TIME_ACCURACY

    neighbor = generate_neighbor(current, CURRENT_LEVEL)

    for i in neighbor:
        current_neighbor_time = calculate_time(i, TIME_ACCURACY)
        if (current_neighbor_time < BEST_SOLUTION_TIME):
            BEST_SOLUTION = i
            BEST_SOLUTION_TIME = current_neighbor_time
            return True

    return False


# Busca local utilizando a estrategia do melhor
# elemento que melhora a solucao atual
def local_search_best(current):

    global CURRENT_LEVEL
    global BEST_SOLUTION
    global BEST_SOLUTION_TIME
    global TIME_ACCURACY

    improved = False
    neighbor = generate_neighbor(current, CURRENT_LEVEL)

    for i in neighbor:
        current_neighbor_time = calculate_time(i, TIME_ACCURACY)
        if (current_neighbor_time < BEST_SOLUTION_TIME):
            BEST_SOLUTION = i
            BEST_SOLUTION_TIME = current_neighbor_time
            improved = True
            
    return improved


# Realiza a leitura de argumentos passados por linha de comando
def read_args():

    global MAX_LEVEL
    global DIR_TF
    global TIME_ACCURACY
    global DIR_TF

    try:
        options, args = getopt.getopt(sys.argv[1:], 'l:d:a:h', ['level=', 'dir=', 'accuracy=', 'help'])

    except getopt.GetoptError as err:
        print('Erro: ' + str(err) )
        sys.exit(2)

    for opt, arg in options:

        if opt in ('-l', '--level'):
            level = int(arg)
            if (level < 1) or (level > 5):
                print('Erro: O nivel maximo deve estar entre 1 e 5.')
                sys.exit() 
            MAX_LEVEL = level

        elif opt in ('-d', '--dir'):
            DIR_TF = arg

        elif opt in ('-a', '--accuracy'):
            TIME_ACCURACY = int(arg)

        elif opt in ('-h', '--help'):
            help()
            sys.exit()


# Exibe mensagem informativa sobre o algoritmo
def help():

    print('\nVISAO GERAL:\nEste script aplica o algoritmo VND (Variable Neighborhood Descent)' +
        ' em conjunto com o Framework TF, para encontrar um bom conjunto de otimizacoes ao' +
        ' utilizar o compilador Clang em determinado programa.')

    print('\nPRE-REQUISITOS:\n- Python (https://www.python.org/)' +
        '\n- Clang (https://clang.llvm.org/)\n- TF Framework (https://github.com/guilhermeleobas/tf.git)')

    print('\nUSO:\n- Primeiramente, este script "VND_Opt_Compile.py" deve estar no diretorio raiz do Framewrok TF' +
        ' (mesmo diretorio em que se encontra o  "run.sh" do TF). Ou entao, configure o diretorio do TF pelo argumento -d ou --dir.' +
        '\n- O Framewrok TF deve estar configurado para compilar e executar apenas um programa.' +
        '\n- Executando: python VND_Opt_Compile.py [opcao] <valor>')

    print('\nOPCOES:\n-l <valor> ou --level <valor>\nNivel maximo: Deve estar entre 1 e 5.' +
        ' Determina qual o nivel maximo de vizinhanca gerada.' +
        ' Quanto maior o nivel, maior sera a vizinhanca gerada, obtendo uma otimizacao mais precisa,' +
        ' com gasto maior de tempo para obte-la. Por padrao o algoritmo executa com nivel maximo = 3.' +
        '\n\n-d <diretorio> ou --dir <diretorio>\nDiretorio do TF: Especifique o diretorio do Framework TF.' +
        ' Por padrao o algoritmo utiliza o diretorio atual.' + 
        '\n\n-a <valor> ou --accuracy <valor>\nPrecisao no tempo de execucao: Determina a precisao ao calcular o ' + 
        'tempo de execucao dos programas compilados. Se accuracy = 2 por exemplo, faz a media de 2 execucoes.' +
        ' Por padrao o algoritmo executa com accuracy = 3.' +
        '\n\n-h ou --help\nExibe mensagem informativa sobre o algoritmo.\n')

    print('\n~ Desenvolvido por William Rodrigues.\n')

# Funcao principal (VND)
def main():

    global CURRENT_LEVEL
    global MAX_LEVEL
    global BEST_SOLUTION
    global BEST_SOLUTION_TIME
    global opt_boolean

    read_args() # Leitura dos argumentos

    generate_opt_arrays() # Inicializa os vetores de otimizacoes

    CURRENT_LEVEL = 1 # Nivel atual
    BEST_SOLUTION = opt_boolean # Melhor solucao (inicia com O3)
    BEST_SOLUTION_TIME = calculate_time(opt_boolean, TIME_ACCURACY) # Tempo da melhor solucao

    log = ('\n\nTempo da solucao inicial (O3): ' + str(BEST_SOLUTION_TIME))

    while CURRENT_LEVEL <= MAX_LEVEL:

        improved = local_search_best(BEST_SOLUTION)

        log += ('\n\nNIVEL atual: ' + str(CURRENT_LEVEL))
        log += ('\nMelhor tempo ate o momento: ' + str(BEST_SOLUTION_TIME))

        if improved == True:
            CURRENT_LEVEL = 1
            continue
        else:
            CURRENT_LEVEL += 1

    print('\nLOG DE EXECUCAO:' + log)
    print('\nMelhor solucao encontrada: \n\n' + opt_boolean_to_names(BEST_SOLUTION, opt_names))
    print('\nTempo de execucao da melhor solucao: ' + str(BEST_SOLUTION_TIME))


# Chamada da funcao principal
if __name__ == "__main__":
    main()
