"""Lo que comparten los cuatro métodos de mutación: el sorteo de los loci y su mutación."""


def sorteados(candidatos, azar, probabilidad):
    """Devuelve los loci candidatos que pasaron su propio sorteo independiente."""
    return candidatos[azar.random(len(candidatos)) < probabilidad]


def mutar_loci(individuo, loci, azar, config, ancho, alto):
    """Muta en el lugar los genes de esos loci y devuelve el mismo individuo."""
    for locus in loci:
        posicion = int(locus)
        gen = individuo.gen(posicion)
        individuo.establecer_gen(posicion, gen.mutar(azar, config, ancho, alto))
    return individuo
