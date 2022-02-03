



def prims(graph, root):#returns a min spanning tree as a adjency list graph
    cur_vertex=root
    tree=[]
    parents=[]
    parents.append(-1000)#parent of root does not exist

    while cur_vertex is not None:
        tree.append(cur_vertex)
        mins=[]
        for parent_vertex in tree:
            vertex_weight_min= min([vertex_weight for vertex_weight in graph.search(parent_vertex) if vertex_weight[0] not in tree],
                    key=lambda vertex_weight: vertex_weight[1], default=None)
            if vertex_weight_min is not None:
                mins.append([parent_vertex, vertex_weight_min])
        
        cur_vertex_weight=min(mins, key=lambda vertex_weight: vertex_weight[1][1], default=None)
        if cur_vertex_weight is not None:
            cur_vertex=cur_vertex_weight[1][0]
            parents.append(cur_vertex_weight[0])
        else:
            cur_vertex=cur_vertex_weight
   

       
    return tree, parents

    


def dfs(visited, graph, node):
    if node not in visited:
        visited.append(node)
        if graph.search(node) is not None:
            for neighbour in graph.search(node):
                dfs(visited, graph, neighbour)



