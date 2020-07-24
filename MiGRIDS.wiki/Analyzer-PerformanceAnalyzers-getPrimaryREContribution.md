Calculates the contribution of renewable generation (variable generation!) to the firm demand. Returns the fraction 'Renewable kWh/Total Firm kWh' as an output.

# Inputs
**time**: [Series] time vector in seconds
**firmLoadP**: [Series] firm load real power vector in kWh
**firmGenP**: [Series] firm generation (load following) real power vector in kWh
**varGenP**: [Series] variable generation (non-load following) real power vector in kWh
# Outputs
**renewableContribution**: [float] fraction of renewable contribution to total firm demand.
   