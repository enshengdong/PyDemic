#ifndef ROW_BUFFER_H_INC
#define ROW_BUFFER_H_INC

#include <memory>
#include <type_traits>

template <class T>
class row_buffer {
private:
    std::unique_ptr<T[]> buffer;
    size_t width_;
    size_t height_;
public:
    template <bool Const>
    class row_t {
        friend class row_t<!Const>;
    public:
        using elem_t = typename std::conditional<Const, const T, T>::type;
        using iterator = elem_t*;

        elem_t& operator[](size_t index) {
            return row_start[index];
        }
        template <bool C = Const>
        row_t(typename std::enable_if<!C, const row_t<true>&>::type other) :
            width(other.width),
            row_start(other.row_start)
        {
            //
        }
        row_t(const row_t<Const>&) = default;
        class iter {
            friend class row_t<!Const>::iter;
            friend class row_buffer<T>;
        public:
            iter(const iter&) = default;
            template <bool C = Const>
            iter(typename std::enable_if<!C, const typename row_t<true>::iter&>::type i) :
                row_start(i.row_start),
                width(i.width)
            {
                //
            }
            typedef elem_t* iterator;
            row_t<Const> operator*() const {
                return row_t<Const>(row_start, width);
            }
            iter& operator++() {
                row_start += width;
                return *this;
            }
            iter operator++(int) {
                iter ret(*this);
                ++(*this);
                return ret;
            }
            iter& operator--() {
                row_start -= width;
                return *this;
            }
            iter operator--(int) {
                iter ret(*this);
                --(*this);
                return ret;
            }
            bool operator!=(const iter& other) const {
                return row_start != other.row_start;
            }
            bool operator==(const iter& other) const {
                return row_start == other.row_start;
            }
        private:
            size_t width;
            elem_t* row_start;
            iter(elem_t* s, size_t w) : width(w), row_start(s) {}
        };
        iterator begin() {
            return row_start;
        }
        iterator end() {
            return row_start + width;
        }
        const iterator cbegin() const {
            return row_start;
        }
        const iterator cend() const {
            return row_start + width;
        }
    private:
        size_t width;
        elem_t* row_start;
        row_t(elem_t* ptr, size_t w) : width(w), row_start(ptr) {}
    };
    template <bool Const>
    friend class all_t_gen;
    template <bool Const>
    class all_t_gen {
        friend class row_buffer<T>;
    private:
        using ref_t = typename std::conditional<Const, const row_buffer<T>&, row_buffer<T>&>::type;
        ref_t ref;
    public:
        using iterator = typename std::conditional<Const, const T*, T*>::type;
        all_t_gen(ref_t r) : ref(r) {}
        all_t_gen(const all_t_gen<Const>&) = default;
        iterator begin() {
            return ref.buffer.get();
        }
        iterator end() {
            return ref.buffer.get() + ref.width_*ref.height_;
        }
    };
    using row = row_t<false>;
    using const_row = row_t<true>;
    using iterator = typename row::iter;
    using const_iterator = typename const_row::iter;
    using all_t = all_t_gen<false>;
    using call_t = all_t_gen<true>;
    using all_iterator = T*;
    using const_all_iterator = const T*;
    iterator begin() {
        return iterator(buffer.get(), width_);
    }
    iterator end() {
        return iterator(buffer.get() + width_*height_, width_);
    }
    const_iterator cbegin() const {
        return const_iterator(buffer.get(), width_);
    }
    const_iterator cend() const {
        return const_iterator(buffer.get() + width_*height_, width_);
    }
    //row, column
    T& operator()(size_t i, size_t j) {
        return buffer[i*width_+j];
    }
    //row, column
    const T& operator()(size_t i, size_t j) const {
        return buffer[i*width_+j];
    }
    row operator[](size_t i) {
        return row(buffer.get() + i*width_, width_);
    }
    const_row operator[](size_t i) const {
        return row(buffer.get() + i*width_, width_);
    }
    all_iterator allbegin() {
        return buffer.get();
    }
    const_all_iterator allcbegin() const {
        return buffer.get();
    }
    all_iterator allend() {
        return buffer.get() + width_*height_;
    }
    const_all_iterator allcend() const {
        return buffer.get() + width_*height_;
    }
    all_t all() {
        return all_t(*this);
    }
    call_t call() const {
        return call_t(*this);
    }
    T* data() {
        return buffer.get();
    }
    const T* data() const {
        return buffer.get();
    }
    size_t height() const {
        return height_;
    }
    size_t width() const {
        return width_;
    }
    row_buffer(size_t w, size_t h) :
        buffer(new T[w*h]),
        width_(w),
        height_(h)
    {
        //
    }
    row_buffer(const row_buffer<T>& other) :
        buffer(new T[other.width_*other.height_]),
        width_(other.width_),
        height_(other.height_)
    {
        std::copy(other.allcbegin(), other.allcend(), allbegin());
    }
    row_buffer(row_buffer<T>&& other) = default;
    ~row_buffer() = default;
        
};

#endif
