CREATE TABLE public.simulated_risk_input (
    -- Foreign key ties each risk observation to a known candidate bond.
    internal_id TEXT NOT NULL
        REFERENCES public.bond_master(internal_id),
    valuation_date DATE NOT NULL,
    -- Effective duration is measured in years.
    effective_duration_years NUMERIC NOT NULL
        CHECK (
            effective_duration_years > 0
            AND effective_duration_years NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ),
    -- Option-adjusted spread is measured in basis points.
    oas_bps NUMERIC NOT NULL
        CHECK (
            oas_bps >= 0
            AND oas_bps NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        ),
    risk_status TEXT NOT NULL
        CHECK (risk_status = 'simulated'),
    -- Composite key allows one risk input per bond on each date.
    PRIMARY KEY (internal_id, valuation_date)
);
