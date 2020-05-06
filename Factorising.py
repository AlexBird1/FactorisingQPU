import dwavebinarycsp as dbc
import time

print("Please Enter a number between 1 and 49 inclusive: ")
P=int(input()) #read in the number to be fastorised and convert to 6 bit binary 
if P <= 49 and P >= 1:
    bP = "{:06b}".format(P)
    print(bP)

    csp = dbc.factories.multiplication_circuit(3) # convert to csp

    bqm = dbc.stitch(csp, min_classical_gap=.1) # convert to bqm

    p_vars = ['p0', 'p1', 'p2', 'p3', 'p4', 'p5']  # converting variables created by the multiplication circuit
    fixed_variables = dict(zip(reversed(p_vars), "{:06b}".format(P)))
    fixed_variables = {var: int(x) for(var, x) in fixed_variables.items()}
    for var, value in fixed_variables.items():
       bqm.fix_variable(var, value)

    start = time.perf_counter() #starting timer 
    from solvers import default_solver #this section creates and runs the solver on the QPU
    my_solver, my_token = default_solver()

    from dwave.system.samplers import DWaveSampler
    sampler = DWaveSampler(solver={'qpu': True}) 
    _, target_edgelist, target_adjacency = sampler.structure

    from dwave.embedding import embed_bqm, unembed_sampleset
    from embedding import embeddings

    embedding = embeddings[sampler.solver.id]
    bqm_embedded = embed_bqm(bqm, embedding, target_adjacency, 3.0)

    kwargs = {}
    if 'num_reads' in sampler.parameters:
        kwargs['num_reads'] = 50
    if 'answer_mode' in sampler.parameters:
        kwargs['answer_mode'] = 'histogram'
    response = sampler.sample(bqm_embedded, **kwargs)
    response = unembed_sampleset(response, embedding, source_bqm=bqm)

    fin = time.perf_counter() #solver is complete so timer ends 

    from convert import to_base_ten
    sample = next(response.samples(n=1))
    dict(sample)
    a, b = to_base_ten(sample)
    print("Given integer P={}, found factors a={} and b={}".format(P, a, b)) #printing out results
    print(f"Number factorised in {fin - start:0.4f} seconds")

else:
    print ("Number not within range")
