
def calcularCapitalMovimiento(valorMovimientoAnterior, tipoMovimientoAnterior, nuevoValorMovimiento, nuevoTipoMovimiento, capitalUsuario):
    nuevoCapital = 0
    if(tipoMovimientoAnterior == nuevoTipoMovimiento):
        if nuevoTipoMovimiento == '1':
            nuevoCapital = capitalUsuario - valorMovimientoAnterior
            nuevoCapital = nuevoCapital + nuevoValorMovimiento
        elif nuevoTipoMovimiento == '2':
            nuevoCapital = capitalUsuario + valorMovimientoAnterior
            nuevoCapital = nuevoCapital - nuevoValorMovimiento
        else:
            nuevoCapital = capitalUsuario       
    
    elif(tipoMovimientoAnterior != nuevoTipoMovimiento):
        if nuevoTipoMovimiento == '1':
            nuevoCapital = capitalUsuario + valorMovimientoAnterior
            nuevoCapital = nuevoCapital + nuevoValorMovimiento
        elif nuevoTipoMovimiento == '2':
            nuevoCapital = capitalUsuario - valorMovimientoAnterior
            nuevoCapital = nuevoCapital - nuevoValorMovimiento
        else:
            nuevoCapital = capitalUsuario     
    else:
        nuevoCapital = capitalUsuario                    

    return nuevoCapital