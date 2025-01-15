##############################################################
#                     Öğrencinin:                            #
#                                                            #
#           Adı:        Akif Emre                            #
#           Soyadı:     Sula                                 #
#           Numarası:   B211210030                           #
#           Şubesi:     1.Öğretim A Grubu                    #
#           Öğretmeni:  Prof.Dr. NEJAT YUMUŞAK               #
#                                                            #
#                                                            #
#                                                            #
#  youtube videolu anlatım: https://youtu.be/Zf8OoK67o4E     #
#                                                            #
##############################################################

# görselleştirme için terminale yazıp çalıştırın:      pip install -r requirements.txt
# uygulamayı çalıştırmak için terminale yazıp entera tıklayın:    python dfa_minimization.py
 
import matplotlib.pyplot as plt
import networkx as nx

def open_file(fileName):
    with open(fileName) as file:
        lines = file.readlines()

    matrix = []
    # Dosyanın son üç satırını özel değerler olduğu için okumaz.
    for line in lines[:-3]:
        line = line.strip().split('->')
        src = int(line[0])  # Kaynak durum
        symbol, dest = line[1].strip('()').split(',')  # Alfabe ve hedef durum

        matrix.append([src, symbol, int(dest)])

    # Başlangıç durumu, kabul durumları ve alfabe bilgisi
    start = int(lines[-3].strip())
    finals = list(map(int, lines[-2].strip().split(',')))
    alpha = lines[-1].strip().split(',')

    return matrix, start, finals, alpha

def make_adjacency_matrix(matrix, alpha):
    nodes = set()
    # Tüm durumları toplar
    for line in matrix:
        nodes.add(line[0])  # kaynak durum
        nodes.add(line[2])  # hedef durum

    nodes = sorted(list(nodes))  # Durumları sıralar
    len_nodes = len(nodes)
    adjancy_matrix = [[-1] * len_nodes for _ in range(len_nodes)]

    node_index = {node: idx for idx, node in enumerate(nodes)}

    for src, symbol, dest in matrix:
        src_idx = node_index[src]
        dest_idx = node_index[dest]

        # Bağlantıyı ekler, gerekiyorsa günceller
        if adjancy_matrix[src_idx][dest_idx] == -1:
            adjancy_matrix[src_idx][dest_idx] = symbol
        elif isinstance(adjancy_matrix[src_idx][dest_idx], list):
            adjancy_matrix[src_idx][dest_idx].append(symbol)
        else:
            adjancy_matrix[src_idx][dest_idx] = [adjancy_matrix[src_idx][dest_idx], symbol]

    return adjancy_matrix

def draw_dfa(matrix, start, finals):
    G = nx.MultiDiGraph()

    for src, symbol, dest in matrix:
        G.add_edge(src, dest, label=str(symbol))

    pos = nx.spring_layout(G, seed=2)

    nx.draw(G, pos, with_labels=True, node_size=1000, node_color="skyblue", font_size=15, font_weight="bold", arrowsize=20)

    edge_labels = {}
    for src, dest, key, data in G.edges(keys=True, data=True):
        label = data['label']
        if (src, dest) in edge_labels:
            edge_labels[(src, dest)] += f", {label}"
        else:
            edge_labels[(src, dest)] = label

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    nx.draw_networkx_nodes(G, pos, nodelist=[start], node_color='green', node_size=900)
    nx.draw_networkx_nodes(G, pos, nodelist=finals, node_color='skyblue', node_size=1000, edgecolors='blue')

    plt.show()

def alpha_check(adjacency_matrix, alpha):
    def flatten(row):
        flat_list = []
        for item in row:
            if isinstance(item, list):
                flat_list.extend(item)
            else:
                flat_list.append(item)
        return flat_list

    for row in adjacency_matrix:
        flat_row = flatten(row)
        if not all(item in flat_row for item in alpha):
            exit(f'Error in adjacency_matrix row: {row}\nalpha_check()')

def remove_unreachable_nodes(matrix, alpha, start):
    reachable_nodes = set()

    def dfs(node):
        reachable_nodes.add(node)
        for src, symbol, dest in matrix:
            if src == node and dest not in reachable_nodes:
                dfs(dest)

    dfs(start)

    new_matrix = [row for row in matrix if row[0] in reachable_nodes and row[2] in reachable_nodes]
    return new_matrix

def finals_non_finals(matrix, finals):
    states = set()
    for src, symbol, dest in matrix:
        states.add(src)
        states.add(dest)

    non_finals = [state for state in states if state not in finals]
    return non_finals, finals

def get_transition_class(state, matrix, equivalence_classes, alpha):
    transition_classes = []
    for symbol in alpha:
        destination = None
        for src, sym, dest in matrix:
            if src == state and sym == symbol:
                destination = dest
                break

        if destination is None:
            transition_classes.append(-1)
        else:
            for idx, eq_class in enumerate(equivalence_classes):
                if destination in eq_class:
                    transition_classes.append(idx)
                    break

    return transition_classes

def refine_equivalence_classes(matrix, finals, alpha):
    non_finals, finals = finals_non_finals(matrix, finals)
    equivalence_classes = [non_finals, finals]

    while True:
        new_classes = []

        for group in equivalence_classes:
            if len(group) <= 1:
                new_classes.append(group)
                continue

            refined_groups = {}
            for state in group:
                state_transitions = tuple(get_transition_class(state, matrix, equivalence_classes, alpha))
                refined_groups.setdefault(state_transitions, []).append(state)

            new_classes.extend(refined_groups.values())

        new_classes = [sorted(group) for group in new_classes]
        new_classes.sort()

        if new_classes == equivalence_classes:
            break

        equivalence_classes = new_classes

    return equivalence_classes

def write_transactions(equivalence_classes, matrix):
    transactions = []

    for group in equivalence_classes:
        for state in group:
            transitions = {}
            for src, symbol, dest in matrix:
                if src == state:
                    transitions.setdefault(symbol, []).append(dest)

            transactions.append((state, transitions))

    return transactions

def visualize_dfa_transactions(equivalence_classes, transactions):
    G = nx.DiGraph()

    for group in equivalence_classes:
        G.add_node(tuple(group))

    for state, transitions in transactions:
        current_group = None
        for group in equivalence_classes:
            if state in group:
                current_group = tuple(group)
                break

        if current_group:
            for symbol, next_states in transitions.items():
                for next_state in next_states:
                    next_group = None
                    for group in equivalence_classes:
                        if next_state in group:
                            next_group = tuple(group)
                            break
                    if next_group:
                        G.add_edge(current_group, next_group, label=str(symbol))

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=1500, node_color='skyblue', font_size=12, font_weight='bold', edge_color='gray')
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title('Minimized DFA Visualization')
    plt.show()

def main():
    matrix, start, finals, alpha = open_file('file.txt')        # Buraya file.txt / file2.txt / file3.txt yazarak farkli DFA modelleri secebilir ya da manuel  
                                                                # olarak file.txt dosyasindaki durumları kendi istediginize gore sekillendirebilirsiniz.     
    draw_dfa(matrix, start, finals)                             # durumlari manuel girerken son 3 satirin sirasiyla:
                                                                # ' baslangic durumu - kabul durumu - alfabe ' oldugunu unutmayiniz.
    adjacency_matrix = make_adjacency_matrix(matrix, alpha)
    alpha_check(adjacency_matrix, alpha)

    shorten_matrix = remove_unreachable_nodes(matrix, alpha, start)

    unreachable_nodes = set(row[0] for row in matrix) - set(row[0] for row in shorten_matrix)
    if unreachable_nodes:
        print(f"Ulasilamayan {unreachable_nodes} Durumu Kaldirildi.")

    equivalence_classes = refine_equivalence_classes(shorten_matrix, finals, alpha)
    print('Denk Durumlar: ', equivalence_classes)

    transactions = write_transactions(equivalence_classes, matrix)
    visualize_dfa_transactions(equivalence_classes, transactions)

if __name__ == '__main__':
    main()


