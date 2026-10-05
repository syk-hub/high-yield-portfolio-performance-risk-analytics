CREATE TABLE public.portfolio_holding (
    -- One portfolio face allocation per known candidate bond.
    internal_id TEXT PRIMARY KEY
        REFERENCES public.bond_master(internal_id),
    -- Face value is stored in USD and must be finite and positive.
    face_value_usd NUMERIC NOT NULL
        CHECK (
            face_value_usd > 0
            AND face_value_usd NOT IN
                ('NaN'::NUMERIC, 'Infinity'::NUMERIC, '-Infinity'::NUMERIC)
        )
);
