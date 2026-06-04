import React, { useState } from "react";
import Select from "react-select";

import { ErrorList } from "./error-list";

const styles = {
    container: (base) => ({
        ...base,
        maxWidth: "30rem",
    }),
    control: (base) => ({
        ...base,
        backgroundColor: "var(--body-bg)",
        color: "var(--body-fg)",
        borderColor: "var(--hairline-color)",
    }),
    menu: (base) => ({
        ...base,
        backgroundColor: "var(--body-bg)",
        color: "var(--body-fg)",
    }),
    option: (base, state) => ({
        ...base,
        backgroundColor: state.isFocused
            ? "var(--selected-row)"
            : "var(--body-bg)",
        color: "var(--body-fg)",
    }),
    singleValue: (base) => ({
        ...base,
        color: "var(--body-fg)",
    }),
    input: (base) => ({
        ...base,
        color: "var(--body-fg)",
    }),
    menuPortal: (base) => ({
        ...base,
        zIndex: 9999,
    }),
};

const SearchableSelectInput = ({
    choices,
    name,
    id,
    label,
    helpText,
    errors,
    initialValue,
    onChange,
}) => {
    const [currentValue, setCurrentValue] = useState(initialValue || "");
    const [_errors] = useState(errors || []);

    const options = choices.map(([value, label]) => ({
        value,
        label,
    }));

    const selected =
        options.find(option => option.value === currentValue) || null;

    return (
        <div>
            <ErrorList errors={_errors} />

            <label className="required" htmlFor={id}>
                {label}
            </label>

            <input
                type="hidden"
                name={name}
                value={currentValue}
            />

            <Select
                styles={styles}
                menuPortalTarget={document.body}
                menuPosition="fixed"
                inputId={id}
                options={options}
                value={selected}
                onChange={(option) => {
                    const value = option ? option.value : "";

                    setCurrentValue(value);

                    if (onChange) {
                        onChange(value);
                    }
                }}
                isSearchable
            />

            {helpText && (
                <div>
                    <span className="help">{helpText}</span>
                </div>
            )}
        </div>
    );
};

export { SearchableSelectInput };