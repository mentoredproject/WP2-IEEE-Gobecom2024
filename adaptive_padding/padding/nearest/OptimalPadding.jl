module OptimalPadding

export n, C, v, discrete_optimal_padding

using CSV, DataFrames, StatsBase

v = CSV.read("Data/OnlyIoT/packet_sizes.csv", DataFrame).Length

# vou usar frequências nos algoritmos (int), e depois divido por lenght(v)
p = countmap(v)

x = sort!(collect(keys(p)))
n = length(x)

# Note que c(i,j) no algoritmo é o mesmo que C[i+1,j] aqui, pois 1o indice começa em zero e os indices em julia começam em 1.
C = zeros(Int64, n+1, n)
function pre_compute_c()
    for j in n:-1:2
        for i in (j-2):-1:0
            C[i+1,j] = C[i+2,j] + p[x[i+1]]*(x[j] - x[i+1])
        end
    end
end
pre_compute_c()

function discrete_optimal_padding(m, n, C)
    d = zeros(Int64, m, n)
    pred = zeros(Int64, m, n)
    
    for j in 2:n
        d[1,j] = C[1,j]
    end
    for m′ in 2:m
        for j in 2:n
            d[m′,j] = typemax(Int64)
            for i in 1:(j-1)
                if C[i+1,j] + d[m′-1,i] < d[m′,j]
                    d[m′,j] = C[i+1,j] + d[m′-1,i]
                    pred[m′,j] = i
                end
            end
        end
    end
    
    y = zeros(Int64, m)
    y[m] = n
    for m′ in (m-1):-1:1
        y[m′] = pred[m′+1, y[m′+1]]
    end
    d[m,n], x[y]
end

end # module OptimalPadding

using .OptimalPadding, BenchmarkTools
m = 10
@show m, n, length(v), mean(v)
@show (padding,_) = discrete_optimal_padding(m, n, C)
@show padding / length(v) / mean(v)

#$ julia --project -L src/OptimalPadding.jl
#@benchmark discrete_optimal_padding($m, $n, $C) samples=1000 seconds=10
