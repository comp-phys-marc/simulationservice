from coefficient import Coefficient, ComplexCoefficient
from models import SinglePhase
import numpy


def actualize(superimposed_state, previous_phase=None):
    
    coefficients = []
    superimposed_state_bits = ""
    negative_flag_bits = ""
    imaginary_flag_bits = ""
    
    for state in superimposed_state.states:
        coefficient = state.get_coefficient()
        
        if isinstance(coefficient, Coefficient):
            coefficients.append(str(coefficient.get_magnitude()))
            superimposed_state_bits += state.get_val()
            negative_flag_bits += int(coefficient.get_magnitude() < 0)
            imaginary_flag_bits += int(coefficient.get_imaginary())
            
        elif isinstance(coefficient, ComplexCoefficient):
            coefficients.append(str(coefficient.get_imaginary_component().get_magnitude()))
            superimposed_state_bits += state.get_val()
            negative_flag_bits += int(coefficient.get_imaginary_component().get_magnitude() < 0)
            imaginary_flag_bits += int(coefficient.get_imaginary_component().get_imaginary())
            
            coefficients.append(str(coefficient.get_real_component().get_magnitude()))
            superimposed_state_bits += state.get_val()
            negative_flag_bits += int(coefficient.get_real_component().get_magnitude() < 0)
            imaginary_flag_bits += int(coefficient.get_real_component().get_imaginary())
    
    shortest = min(coefficients, key=len)
    divisions = len(shortest)
    
    relative_sizes = list(map(lambda coefficient: int(len(coefficient)/divisions), coefficients))
    
    a = ""
    i = 0
    while i < divisions:
        for j in range(len(coefficients)):
            coefficient = coefficients[j]
            a += coefficient[i*relative_sizes[j]:(i+1)*relative_sizes[j]]
        i += 1
        
    [phi, theta] = encode(a=int(a), b=0, g=1)
    
    if previous_phase is not None:
        previous_phase_id = previous_phase.id
    else:
        previous_phase_id = -1

    print("\nstate register: {0}\nnegative flag register: {1}\nimaginary flag register: {2}\nphase: {3}\n"
          .format(phi, negative_flag_bits, imaginary_flag_bits, superimposed_state_bits))
        
    return SinglePhase(
        phase=phi,
        negative_flags=negative_flag_bits, 
        imaginary_flags=imaginary_flag_bits, 
        states=superimposed_state_bits,
        previous_phase_id=previous_phase_id
    )


def encode(a, b, g):
    radius = a + (a/(2*g))
    dz = numpy.absolute(((2*(a**2+a)-1) + numpy.sqrt(numpy.absolute((2*(a**2+a)-1)**2 - 4*((a**2+a)**2+1/4-(a+a/(2*g))**2))))/2 - ((2*(a**2+a)-1) - numpy.sqrt(numpy.absolute((2*(a**2+a)-1)**2 - 4*((a**2+a)**2+1/4-(a+a/(2*g))**2))))/2)
    dx = numpy.absolute(a - (-1+numpy.sqrt(numpy.absolute(1-4*g*(((2*(a**2+a)-1)) - numpy.sqrt(numpy.absolute((2*(a**2+a)-1)**2 - 4*((a**2+a)**2+1/4-(a+a/(2*g))**2))))/2))/(2*g)))
    c = numpy.sqrt(dx**2+dz**2)
    phi = numpy.arcsin(c*numpy.sin(numpy.pi - numpy.arcsin(dx/c))/radius)
    theta = numpy.arcsin(b)
    
    return numpy.array([phi, theta])


def decode(phi, theta, g):
    c = numpy.sqrt(2-2*numpy.cos(phi))
    alpha = - numpy.arcsin(numpy.sin(phi)/c)+numpy.pi/2
    beta = numpy.pi - numpy.pi/2 - alpha
    dx = c*numpy.sin(alpha)
    dz = c*numpy.sin(beta)
    b = numpy.sin(theta)
    x = (dz/dx-1-g*b**2-b)/(2*g)
    a = numpy.ceil(x)
    
    return numpy.array([a, b])